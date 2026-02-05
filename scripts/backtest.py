#!/usr/bin/env python3
"""
Backtesting Script for MVP Trading Bot

This script allows you to backtest trading strategies on historical data
to evaluate their performance before deploying them in paper or live trading.

Usage:
    python scripts/backtest.py --strategy sma_crossover --symbol BTC/USDT --start 2023-01-01 --end 2023-12-31
    python scripts/backtest.py --strategy custom_strategy --config config/strategies/custom.json --days 90
    python scripts/backtest.py --all-strategies --symbol ETH/USDT --days 30
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.utils import get_logger, ConfigLoader
from bot.strategies import get_strategy_class
from bot.brokers import get_broker_class

logger = get_logger(__name__)


class Backtester:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_capital: float = 10000, commission: float = 0.001):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital for backtest
            commission: Trading commission/fee percentage (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.reset()
        
    def reset(self):
        """Reset backtester state"""
        self.capital = self.initial_capital
        self.position = None
        self.entry_price = None
        self.trades = []
        self.equity_curve = []
        
    def run_backtest(
        self,
        strategy: Any,
        data: pd.DataFrame,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data
        
        Args:
            strategy: Strategy instance to backtest
            data: Historical OHLCV data
            symbol: Trading symbol
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest for {strategy.name} on {symbol}")
        logger.info(f"Data range: {data.index[0]} to {data.index[-1]}")
        logger.info(f"Number of candles: {len(data)}")
        
        self.reset()
        
        # Calculate indicators
        data = strategy.calculate_indicators(data)
        
        # Run through each candle
        for i in range(len(data)):
            current_data = data.iloc[:i+1].copy()
            current_price = data.iloc[i]['close']
            timestamp = data.index[i]
            
            # Skip if not enough data for indicators
            if len(current_data) < 20:
                self.equity_curve.append({
                    'timestamp': timestamp,
                    'equity': self.capital,
                    'position': None
                })
                continue
            
            # Check exit conditions
            if self.position is not None:
                if strategy.should_exit(current_data, current_price):
                    self._close_position(current_price, timestamp, 'Exit Signal')
            
            # Check entry conditions
            if self.position is None and strategy.should_enter(current_data):
                signal = strategy.generate_signal(current_data)
                if signal in ['BUY', 'SELL']:
                    position_type = 'LONG' if signal == 'BUY' else 'SHORT'
                    self._open_position(position_type, current_price, timestamp)
                    strategy.enter_position(position_type, current_price)
            
            # Track equity
            equity = self._calculate_equity(current_price)
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': equity,
                'position': self.position
            })
        
        # Close any open position at end
        if self.position is not None:
            final_price = data.iloc[-1]['close']
            final_timestamp = data.index[-1]
            self._close_position(final_price, final_timestamp, 'End of Backtest')
        
        # Calculate results
        results = self._calculate_results()
        return results
    
    def _open_position(self, position_type: str, price: float, timestamp):
        """Open a position"""
        self.position = position_type
        self.entry_price = price
        
        logger.info(f"[{timestamp}] Opened {position_type} position at {price}")
    
    def _close_position(self, price: float, timestamp, reason: str):
        """Close a position"""
        if self.position is None:
            return
        
        # Calculate P&L
        if self.position == 'LONG':
            pnl_pct = ((price - self.entry_price) / self.entry_price) - (2 * self.commission)
        else:  # SHORT
            pnl_pct = ((self.entry_price - price) / self.entry_price) - (2 * self.commission)
        
        pnl = self.capital * pnl_pct
        self.capital += pnl
        
        # Record trade
        trade = {
            'entry_time': self.trades[-1]['entry_time'] if self.trades else timestamp,
            'exit_time': timestamp,
            'position_type': self.position,
            'entry_price': self.entry_price,
            'exit_price': price,
            'pnl': pnl,
            'pnl_pct': pnl_pct * 100,
            'reason': reason
        }
        
        if not self.trades:
            trade['entry_time'] = timestamp
        
        self.trades.append(trade)
        
        logger.info(f"[{timestamp}] Closed {self.position} position at {price} | P&L: ${pnl:.2f} ({pnl_pct*100:.2f}%) | Reason: {reason}")
        
        self.position = None
        self.entry_price = None
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate current equity including open position"""
        if self.position is None:
            return self.capital
        
        # Calculate unrealized P&L
        if self.position == 'LONG':
            unrealized_pnl_pct = (current_price - self.entry_price) / self.entry_price
        else:  # SHORT
            unrealized_pnl_pct = (self.entry_price - current_price) / self.entry_price
        
        unrealized_pnl = self.capital * unrealized_pnl_pct
        return self.capital + unrealized_pnl
    
    def _calculate_results(self) -> Dict[str, Any]:
        """Calculate backtest performance metrics"""
        if not self.trades:
            logger.warning("No trades executed during backtest")
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_return': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'profit_factor': 0
            }
        
        # Basic stats
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['pnl'] > 0])
        losing_trades = len([t for t in self.trades if t['pnl'] <= 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # P&L stats
        total_pnl = sum(t['pnl'] for t in self.trades)
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        avg_win = np.mean([t['pnl'] for t in self.trades if t['pnl'] > 0]) if winning_trades > 0 else 0
        avg_loss = abs(np.mean([t['pnl'] for t in self.trades if t['pnl'] <= 0])) if losing_trades > 0 else 0
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in self.trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in self.trades if t['pnl'] <= 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Max drawdown
        equity_series = pd.Series([e['equity'] for e in self.equity_curve])
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Sharpe ratio (simplified - assumes daily returns)
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0
        
        results = {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        return results


def fetch_historical_data(
    broker: Any,
    symbol: str,
    timeframe: str,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data from broker
    
    Args:
        broker: Broker instance
        symbol: Trading symbol
        timeframe: Timeframe (1m, 5m, 1h, 1d, etc.)
        start_date: Start date
        end_date: End date
        
    Returns:
        DataFrame with OHLCV data
    """
    logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
    
    try:
        # Calculate number of candles needed
        since = int(start_date.timestamp() * 1000)
        
        all_data = []
        current_since = since
        end_timestamp = int(end_date.timestamp() * 1000)
        
        while current_since < end_timestamp:
            # Fetch batch of data
            ohlcv = broker.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=current_since,
                limit=1000
            )
            
            if not ohlcv:
                break
            
            all_data.extend(ohlcv)
            
            # Update since to last candle timestamp
            current_since = ohlcv[-1][0] + 1
            
            # Break if we've reached the end
            if len(ohlcv) < 1000:
                break
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        logger.info(f"Fetched {len(df)} candles")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}", exc_info=True)
        return pd.DataFrame()


def print_results(strategy_name: str, symbol: str, results: Dict[str, Any]):
    """Print backtest results in a formatted table"""
    print("\n" + "=" * 80)
    print(f"BACKTEST RESULTS: {strategy_name} on {symbol}")
    print("=" * 80)
    print(f"Initial Capital:       ${results['initial_capital']:,.2f}")
    print(f"Final Capital:         ${results['final_capital']:,.2f}")
    print(f"Total P&L:             ${results['total_pnl']:,.2f}")
    print(f"Total Return:          {results['total_return']:.2f}%")
    print("-" * 80)
    print(f"Total Trades:          {results['total_trades']}")
    print(f"Winning Trades:        {results['winning_trades']}")
    print(f"Losing Trades:         {results['losing_trades']}")
    print(f"Win Rate:              {results['win_rate']:.2f}%")
    print("-" * 80)
    print(f"Average Win:           ${results['avg_win']:,.2f}")
    print(f"Average Loss:          ${results['avg_loss']:,.2f}")
    print(f"Profit Factor:         {results['profit_factor']:.2f}")
    print(f"Max Drawdown:          {results['max_drawdown']:.2f}%")
    print(f"Sharpe Ratio:          {results['sharpe_ratio']:.2f}")
    print("=" * 80)
    
    # Print individual trades if requested
    if results['total_trades'] > 0:
        print("\nLast 10 Trades:")
        print("-" * 80)
        for trade in results['trades'][-10:]:
            print(f"{trade['exit_time']} | {trade['position_type']:5s} | "
                  f"Entry: ${trade['entry_price']:,.2f} | Exit: ${trade['exit_price']:,.2f} | "
                  f"P&L: ${trade['pnl']:,.2f} ({trade['pnl_pct']:+.2f}%) | {trade['reason']}")


def save_results(results: Dict[str, Any], output_file: str):
    """Save backtest results to JSON file"""
    # Convert timestamps to strings for JSON serialization
    results_copy = results.copy()
    results_copy['trades'] = [
        {**trade, 'entry_time': str(trade['entry_time']), 'exit_time': str(trade['exit_time'])}
        for trade in results_copy['trades']
    ]
    results_copy['equity_curve'] = [
        {**eq, 'timestamp': str(eq['timestamp'])}
        for eq in results_copy['equity_curve']
    ]
    
    with open(output_file, 'w') as f:
        json.dump(results_copy, f, indent=2)
    
    logger.info(f"Results saved to {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Backtest trading strategies')
    parser.add_argument('--strategy', type=str, help='Strategy name to backtest')
    parser.add_argument('--all-strategies', action='store_true', help='Backtest all active strategies')
    parser.add_argument('--symbol', type=str, default='BTC/USDT', help='Trading symbol')
    parser.add_argument('--timeframe', type=str, default='1h', help='Timeframe (1m, 5m, 1h, 1d)')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, help='Number of days back from today')
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    parser.add_argument('--commission', type=float, default=0.001, help='Commission rate (0.001 = 0.1%%)')
    parser.add_argument('--broker', type=str, default='binance', help='Broker to use for data')
    parser.add_argument('--output', type=str, help='Output file for results (JSON)')
    parser.add_argument('--config', type=str, help='Custom strategy config file')
    
    args = parser.parse_args()
    
    # Determine date range
    if args.days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
    elif args.start and args.end:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    else:
        # Default: last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Load configuration
    config_loader = ConfigLoader()
    
    # Initialize broker for data fetching
    broker_config = config_loader.load_broker_config(args.broker)
    broker_class = get_broker_class(args.broker)
    
    if broker_class is None:
        logger.error(f"Broker not found: {args.broker}")
        return
    
    broker = broker_class(broker_config)
    if not broker.connect():
        logger.error(f"Failed to connect to broker: {args.broker}")
        return
    
    # Fetch historical data
    data = fetch_historical_data(broker, args.symbol, args.timeframe, start_date, end_date)
    
    if data.empty:
        logger.error("No historical data available")
        return
    
    # Initialize backtester
    backtester = Backtester(initial_capital=args.capital, commission=args.commission)
    
    # Determine which strategies to backtest
    if args.all_strategies:
        strategy_config = config_loader.load_strategy_config()
        strategy_names = strategy_config.get('active_strategies', [])
    elif args.strategy:
        strategy_names = [args.strategy]
    else:
        logger.error("Please specify --strategy or --all-strategies")
        return
    
    # Run backtests
    for strategy_name in strategy_names:
        logger.info(f"\nBacktesting strategy: {strategy_name}")
        
        # Load strategy config
        if args.config:
            with open(args.config, 'r') as f:
                strategy_config = json.load(f)
        else:
            all_strategies = config_loader.load_strategy_config()
            strategy_config = all_strategies.get('strategies', {}).get(strategy_name, {})
        
        if not strategy_config:
            logger.warning(f"Config not found for strategy: {strategy_name}")
            continue
        
        # Get strategy class
        strategy_class = get_strategy_class(strategy_name)
        if strategy_class is None:
            logger.warning(f"Strategy class not found: {strategy_name}")
            continue
        
        # Initialize strategy
        strategy = strategy_class(strategy_config)
        
        # Run backtest
        results = backtester.run_backtest(strategy, data, args.symbol)
        
        # Print results
        print_results(strategy_name, args.symbol, results)
        
        # Save results if output file specified
        if args.output:
            output_file = args.output.replace('.json', f'_{strategy_name}.json')
            save_results(results, output_file)
    
    broker.disconnect()
    logger.info("\nBacktesting complete!")


if __name__ == '__main__':
    main()
