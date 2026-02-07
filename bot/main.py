"""
Main trading bot application
"""

import time
import signal
import sys
import argparse
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd

from .utils import get_logger, ConfigLoader
from .brokers import get_broker_class
from .strategies import get_strategy_class
from .core import PortfolioManager, RiskManager, OrderManager, DataManager

logger = get_logger(__name__)


class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self):
        """Initialize the trading bot"""
        logger.info("Initializing MVP Trading Bot")
        
        # Load configuration
        self.config_loader = ConfigLoader()
        self.global_config = self.config_loader.load_global_config()
        self.strategy_config = self.config_loader.load_strategy_config()
        
        # Operating mode
        self.mode = self.global_config.get('mode', 'paper')
        logger.info(f"Bot mode: {self.mode}")
        
        # Initialize components
        self.brokers = {}
        self.strategies = {}
        self.portfolio = PortfolioManager(mode=self.mode)
        self.risk_manager = RiskManager(self.global_config.get('risk_management', {}))
        self.order_manager = OrderManager(mode=self.mode)
        self.data_manager = DataManager()
        
        # Runtime state
        self.running = False
        self.update_interval = self.global_config.get('execution', {}).get('update_interval', 60)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize(self) -> bool:
        """
        Initialize brokers and strategies
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize brokers
            enabled_brokers = self.config_loader.get_enabled_brokers()
            logger.info(f"Initializing {len(enabled_brokers)} broker(s)")
            
            for broker_name in enabled_brokers:
                broker_config = self.config_loader.load_broker_config(broker_name)
                broker_class = get_broker_class(broker_name)
                
                if broker_class is None:
                    logger.warning(f"Broker class not found for {broker_name}")
                    continue
                
                broker = broker_class(broker_config)
                if broker.connect():
                    self.brokers[broker_name] = broker
                    self.data_manager.set_broker(broker_name, broker)
                    logger.info(f"Successfully initialized broker: {broker_name}")
                else:
                    logger.error(f"Failed to connect to broker: {broker_name}")
            
            if not self.brokers:
                logger.error("No brokers connected!")
                return False
            
            # Initialize strategies
            active_strategies = self.strategy_config.get('active_strategies', [])
            strategies_config = self.strategy_config.get('strategies', {})
            
            logger.info(f"Initializing {len(active_strategies)} strateg(ies)")
            
            for strategy_name in active_strategies:
                if strategy_name not in strategies_config:
                    logger.warning(f"Strategy config not found: {strategy_name}")
                    continue
                
                strategy_cfg = strategies_config[strategy_name]
                
                if not strategy_cfg.get('enabled', True):
                    logger.info(f"Strategy disabled: {strategy_name}")
                    continue
                
                strategy_class = get_strategy_class(strategy_name)
                
                if strategy_class is None:
                    logger.warning(f"Strategy class not found for {strategy_name}")
                    continue
                
                strategy = strategy_class(strategy_cfg)
                self.strategies[strategy_name] = strategy
                logger.info(f"Initialized strategy: {strategy_name}")
            
            if not self.strategies:
                logger.warning("No strategies initialized!")
                return False
            
            logger.info("Bot initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def start(self, test_connection_only=False):
        """Start the trading bot"""
        if not self.initialize():
            logger.error("Failed to initialize bot")
            return False
        
        if test_connection_only:
            logger.info("✅ Connection test successful!")
            logger.info(f"Connected brokers: {list(self.brokers.keys())}")
            logger.info(f"Initialized strategies: {list(self.strategies.keys())}")
            self.stop()
            return True
        
        logger.info("Starting trading bot...")
        self.running = True
        
        try:
            while self.running:
                self._run_cycle()
                time.sleep(self.update_interval)
                
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
        finally:
            self.stop()
        
        return True
    
    def _run_cycle(self):
        """Execute one trading cycle"""
        try:
            logger.debug("Running trading cycle")
            
            # Update portfolio with current broker balances
            for broker_name, broker in self.brokers.items():
                try:
                    balance = broker.get_balance()
                    # Portfolio update logic here
                except Exception as e:
                    logger.error(f"Error fetching balance from {broker_name}: {e}")
            
            # Execute strategies
            for strategy_name, strategy in self.strategies.items():
                try:
                    self._execute_strategy(strategy_name, strategy)
                except Exception as e:
                    logger.error(f"Error executing strategy {strategy_name}: {e}", exc_info=True)
            
            # Log portfolio status
            status = self.portfolio.to_dict()
            logger.debug(f"Portfolio value: {status.get('total_value', 0)}")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def _execute_strategy(self, strategy_name: str, strategy: Any):
        """
        Execute a single strategy
        
        Args:
            strategy_name: Name of the strategy
            strategy: Strategy instance
        """
        # Get symbol for this strategy
        symbol = strategy.parameters.get('symbol', 'BTC/USDT')
        
        # Get broker for this symbol (use first available)
        broker_name = next(iter(self.brokers.keys()))
        broker = self.brokers[broker_name]
        
        # Fetch market data
        data = self.data_manager.fetch_ohlcv(
            symbol=symbol,
            timeframe=self.global_config.get('data', {}).get('timeframe', '1h'),
            limit=self.global_config.get('data', {}).get('lookback_period', 100),
            broker_name=broker_name
        )
        
        if data is None or not data:
            logger.warning(f"No data available for {symbol}")
            return
        
        # Convert to DataFrame for indicators calculation
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calculate indicators
        df = strategy.calculate_indicators(df)
        
        # Get current price
        ticker = broker.get_ticker(symbol)
        current_price = ticker.get('last', ticker.get('close', 0))
        
        # Check if should exit current position
        if strategy.should_exit(df, current_price):
            self._close_position(strategy_name, strategy, broker, symbol, current_price)
        
        # Check if should enter new position
        elif strategy.should_enter(df):
            signal = strategy.generate_signal(df)
            if signal in ['BUY', 'SELL']:
                self._open_position(strategy_name, strategy, broker, symbol, signal, current_price)
    
    def _open_position(
        self,
        strategy_name: str,
        strategy: Any,
        broker: Any,
        symbol: str,
        signal: str,
        price: float
    ):
        """
        Open a new position
        
        Args:
            strategy_name: Name of strategy
            strategy: Strategy instance
            broker: Broker instance
            symbol: Trading symbol
            signal: 'BUY' or 'SELL'
            price: Current price
        """
        # Calculate position size
        position_size = strategy.get_position_size()
        
        # Check risk limits
        if not self.risk_manager.can_open_position(position_size, price):
            logger.warning(f"Risk limits prevent opening position for {strategy_name}")
            return
        
        # Create order
        side = 'buy' if signal == 'BUY' else 'sell'
        order_type = 'market' if self.mode == 'live' else 'limit'
        
        try:
            if self.mode == 'paper':
                # Paper trading - simulate order
                logger.info(f"[PAPER] {signal} {position_size} {symbol} at {price}")
                position_type = 'LONG' if signal == 'BUY' else 'SHORT'
                strategy.enter_position(position_type, price)
                self.portfolio.add_position(symbol, position_type, position_size, price)
            else:
                # Live trading
                order = self.order_manager.create_order(
                    broker=broker,
                    symbol=symbol,
                    order_type=order_type,
                    side=side,
                    amount=position_size / price,  # Convert to quantity
                    price=price if order_type == 'limit' else None
                )
                
                if order:
                    position_type = 'LONG' if signal == 'BUY' else 'SHORT'
                    strategy.enter_position(position_type, price)
                    self.portfolio.add_position(symbol, position_type, position_size, price)
                    logger.info(f"Opened {position_type} position: {symbol}")
                
        except Exception as e:
            logger.error(f"Failed to open position: {e}", exc_info=True)
    
    def _close_position(
        self,
        strategy_name: str,
        strategy: Any,
        broker: Any,
        symbol: str,
        price: float
    ):
        """
        Close an existing position
        
        Args:
            strategy_name: Name of strategy
            strategy: Strategy instance
            broker: Broker instance
            symbol: Trading symbol
            price: Current price
        """
        try:
            if self.mode == 'paper':
                # Paper trading - simulate close
                logger.info(f"[PAPER] Closing position for {symbol} at {price}")
                pnl = self.portfolio.close_position(symbol, price)
                strategy.exit_position()
                logger.info(f"Position closed. PnL: {pnl}")
            else:
                # Live trading - close position
                position = self.portfolio.get_position(symbol)
                if position:
                    side = 'sell' if position['type'] == 'LONG' else 'buy'
                    amount = position['amount']
                    
                    order = self.order_manager.create_order(
                        broker=broker,
                        symbol=symbol,
                        order_type='market',
                        side=side,
                        amount=amount,
                        price=None
                    )
                    
                    if order:
                        pnl = self.portfolio.close_position(symbol, price)
                        strategy.exit_position()
                        logger.info(f"Position closed. PnL: {pnl}")
                        
        except Exception as e:
            logger.error(f"Failed to close position: {e}", exc_info=True)
    
    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping trading bot...")
        self.running = False
        
        # Disconnect brokers
        for broker_name, broker in self.brokers.items():
            try:
                broker.disconnect()
                logger.info(f"Disconnected from {broker_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {broker_name}: {e}")
        
        # Save portfolio state
        try:
            portfolio_state = self.portfolio.to_dict()
            logger.info(f"Final portfolio state: {portfolio_state}")
        except Exception as e:
            logger.error(f"Error saving portfolio state: {e}")
        
        logger.info("Trading bot stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}")
        self.running = False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='MVP Trading Bot')
    parser.add_argument('--test-connection', action='store_true',
                        help='Test broker connection and exit')
    parser.add_argument('--paper-trading', action='store_true',
                        help='Run in paper trading mode')
    parser.add_argument('--dry-run', action='store_true',
                        help='Dry run mode (no orders placed)')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("MVP Trading Bot v1.0.0")
    logger.info("=" * 60)
    
    bot = TradingBot()
    
    if args.test_connection:
        success = bot.start(test_connection_only=True)
        sys.exit(0 if success else 1)
    else:
        bot.start()


if __name__ == '__main__':
    main()
