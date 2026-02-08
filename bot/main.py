"""
Main trading bot application
"""

import time
import signal
import sys
import argparse
import threading
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd

from .utils import get_logger, ConfigLoader
from .brokers import get_broker_class
from .strategies import get_strategy_class
from .core import (
    PortfolioManager, RiskManager, OrderManager, DataManager,
    TradeStateManager,
    RiskEngineV2,
    ExecutionGuardrailsManagerV2,
    RangeAnalyzer,
)

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
        
        # Initialize enhanced components
        self.trade_state_manager = TradeStateManager(
            self.strategy_config.get('trade_management', {})
        )
        
        self.risk_engine_v2 = RiskEngineV2(
            self.global_config.get('risk_management', {})
        )
        
        self.execution_guardrails = ExecutionGuardrailsManagerV2(
            self.global_config.get('execution', {})
        )
        
        self.range_analyzer = RangeAnalyzer(
            self.global_config.get('range_engine', {})
        )
        
        # Runtime state
        self.running = False
        self.update_interval = self.global_config.get('execution', {}).get('update_interval', 60)
        self._cycle_count = 0
        
        # Setup signal handlers (main thread only)
        if threading.current_thread() is threading.main_thread():
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
                try:
                    self._run_cycle()
                    # Use small sleep intervals so Ctrl+C works faster
                    for _ in range(int(self.update_interval)):
                        if not self.running:
                            break
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received")
                    self.running = False
                    break
                    
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
        finally:
            self.stop()
        
        return True
    
    def _run_cycle(self):
        """Execute one trading cycle"""
        try:
            logger.debug("Running trading cycle")
            self._cycle_count += 1
            
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
            
            # Log periodic monitoring stats (every 10 cycles)
            if self._cycle_count % 10 == 0:
                self._log_monitoring_stats()
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def _execute_strategy(self, strategy_name: str, strategy: Any):
        """
        Execute a single strategy with full validation, risk checks, and guardrails
        """
        try:
            symbol = strategy.parameters.get('symbol', 'BTC/USDT')
            broker_name = next(iter(self.brokers.keys()))
            broker = self.brokers[broker_name]
            
            if not broker:
                logger.warning(f"No broker available for {symbol}")
                return
            
            # ========== STEP 1: FETCH MARKET DATA ==========
            data = self.data_manager.fetch_ohlcv(
                symbol=symbol,
                timeframe=self.global_config.get('data', {}).get('timeframe', '15m'),
                limit=self.global_config.get('data', {}).get('lookback_period', 100),
                broker_name=broker_name
            )
            
            if data is None or not data:
                logger.warning(f"No data available for {symbol}")
                return
            
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # ========== STEP 2: ANALYZE RANGE ==========
            analysis = self.range_analyzer.analyze(symbol, df)
            
            can_trade, range_reason = self.range_analyzer.can_trade(analysis)
            if not can_trade:
                logger.debug(f"{symbol}: {range_reason} - skipping this cycle")
                return
            
            # ========== STEP 3: GET STRATEGY SIGNAL ==========
            signal = strategy.generate_signal(df)
            
            ticker = broker.get_ticker(symbol)
            current_price = ticker.get('last', ticker.get('close', 0))
            bid = ticker.get('bid', current_price * 0.99)
            ask = ticker.get('ask', current_price * 1.01)
            
            # ========== STEP 4: CHECK IF ENTERING NEW TRADE ==========
            if signal in ['BUY', 'SELL']:
                # Can we enter a new trade for this symbol?
                can_enter, cooldown_reason = self.trade_state_manager.can_enter_trade(symbol)
                
                if not can_enter:
                    logger.debug(f"{symbol}: {cooldown_reason}")
                    return
                
                # ========== STEP 5: RISK VALIDATION ==========
                # Calculate position size (strategy or default)
                position_size = strategy.get_position_size() if hasattr(strategy, 'get_position_size') else 0.1
                
                # Convert to quantity
                qty = position_size / current_price if current_price > 0 else 0
                
                can_open, risk_reason = self.risk_engine_v2.can_open_position(
                    symbol=symbol,
                    direction=signal,
                    qty=qty,
                    entry_price=current_price
                )
                
                if not can_open:
                    logger.warning(f"{symbol}: Risk blocked - {risk_reason}")
                    return
                
                # ========== STEP 6: EXECUTE WITH GUARDRAILS ==========
                success, error, result = self.execution_guardrails.validate_and_execute(
                    broker=broker,
                    symbol=symbol,
                    side=signal,
                    qty=qty,
                    bid=bid,
                    ask=ask
                )
                
                if success:
                    # ========== STEP 7: OPEN TRADE IN TRACKING SYSTEMS ==========
                    # Record in trade state manager
                    trade = self.trade_state_manager.open_trade(
                        symbol=symbol,
                        direction=signal,
                        entry_price=current_price,
                        position_size=qty,
                        range_position=analysis['range_position'],
                        volatility=analysis['volatility_pct']
                    )
                    
                    # Record in risk engine
                    self.risk_engine_v2.open_position(
                        symbol=symbol,
                        direction=signal,
                        qty=qty,
                        entry_price=current_price
                    )
                    
                    # Record in portfolio
                    self.portfolio.add_position(symbol, signal, qty, current_price)
                    
                    logger.info(
                        f"✅ TRADE OPENED | {symbol} {signal} {qty:.4f} @ ${current_price:.2f} | "
                        f"Range pos: {analysis['range_position']:.1%}"
                    )
                else:
                    logger.warning(f"❌ {symbol} execution failed: {error}")
            
            # ========== STEP 8: MANAGE EXISTING TRADE ==========
            current_trade = self.trade_state_manager.get_current_trade(symbol)
            
            if current_trade:
                # Calculate how long we've been in trade
                candles_since_entry = len(df) - (current_trade.entry_candle_index or 0)
                
                # Advance VG checkpoints
                self.trade_state_manager.advance_checkpoint(symbol, candles_since_entry)
                
                # Check exit conditions
                exit_signal = strategy.manage_trade(df) if hasattr(strategy, 'manage_trade') else None
                
                # Check for volatility exhaustion
                should_exit_exhaustion, exhaustion_reason = self.range_analyzer.should_exit_on_exhaustion(analysis)
                
                if exit_signal == 'EXIT' or should_exit_exhaustion or candles_since_entry > 50:
                    # Get exit price
                    exit_ticker = broker.get_ticker(symbol)
                    exit_price = exit_ticker.get('last', current_price)
                    exit_bid = exit_ticker.get('bid', exit_price * 0.99)
                    exit_ask = exit_ticker.get('ask', exit_price * 1.01)
                    
                    # Close position
                    close_side = "SELL" if current_trade.direction == "BUY" else "BUY"
                    
                    success, error, _ = self.execution_guardrails.validate_and_execute(
                        broker=broker,
                        symbol=symbol,
                        side=close_side,
                        qty=current_trade.position_size,
                        bid=exit_bid,
                        ask=exit_ask
                    )
                    
                    if success:
                        # Close in trade state manager
                        exit_reason = exhaustion_reason or exit_signal or "Timeout"
                        closed_trade = self.trade_state_manager.close_trade(
                            symbol=symbol,
                            exit_price=exit_price,
                            reason=exit_reason
                        )
                        
                        # Close in risk engine
                        self.risk_engine_v2.close_position(
                            symbol=symbol,
                            exit_price=exit_price,
                            reason=exit_reason
                        )
                        
                        # Close in portfolio
                        self.portfolio.close_position(symbol, exit_price)
                        
                        logger.info(
                            f"✅ TRADE CLOSED | {symbol} {closed_trade.direction} | "
                            f"PnL: ${closed_trade.pnl:.2f} ({closed_trade.pnl_pct:.2f}%) | "
                            f"Reason: {exit_reason}"
                        )
                    else:
                        logger.warning(f"❌ {symbol} close failed: {error}")
            
            # Decrement cooldowns each cycle
            self.trade_state_manager.decrement_cooldowns()
            
        except Exception as e:
            logger.error(f"Error executing strategy {strategy_name}: {e}", exc_info=True)
    
    def _log_monitoring_stats(self):
        """Log current monitoring statistics"""
        try:
            # Risk stats
            risk_stats = self.risk_engine_v2.get_stats()
            exposure = self.risk_engine_v2.get_current_exposure()
            
            # Execution stats
            exec_stats = self.execution_guardrails.get_execution_stats()
            
            # Trade stats
            trade_stats = self.trade_state_manager.get_stats()
            
            logger.info(
                f"📊 MONITORING | Balance: ${risk_stats.get('current_balance', 0):.2f} | "
                f"Trades: {trade_stats['total_trades']} "
                f"(W:{trade_stats['winning_trades']} L:{trade_stats['losing_trades']}) | "
                f"Exposure: ${exposure['total_exposure']:.0f} | "
                f"Exec rate: {100-exec_stats['rejection_rate']:.1f}%"
            )
        except Exception as e:
            logger.error(f"Error logging stats: {e}")
    

    
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
        # Raise KeyboardInterrupt to break out of sleep
        raise KeyboardInterrupt("Signal received")


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
