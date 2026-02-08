"""
Backtesting Engine - Test strategies on historical data
Validates win rate, expectancy, max drawdown before live trading
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from decimal import Decimal
import threading

from ..utils.logger import get_logger
from .range_engine import RangeAnalyzer, ZoneClassifier
from .trade_state_manager import TradeStateManager

logger = get_logger(__name__)


class BacktestMetrics:
    """Container for backtest results"""
    
    def __init__(self):
        self.trades: List[Dict[str, Any]] = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.win_rate = 0.0
        self.total_pnl = 0.0
        self.avg_pnl_per_trade = 0.0
        self.max_win = 0.0
        self.max_loss = 0.0
        self.expectancy = 0.0  # Average PnL
        self.sharpe_ratio = 0.0
        self.max_drawdown = 0.0
        self.max_drawdown_pct = 0.0
        self.start_balance = 0.0
        self.end_balance = 0.0
        self.total_return_pct = 0.0
        self.num_signals = 0
        self.num_rejected = 0
        self.rejection_rate = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": f"{self.win_rate:.1f}%",
            "total_pnl": f"${self.total_pnl:.2f}",
            "avg_pnl": f"${self.avg_pnl_per_trade:.2f}",
            "max_win": f"${self.max_win:.2f}",
            "max_loss": f"${self.max_loss:.2f}",
            "expectancy": f"${self.expectancy:.2f}",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "max_drawdown": f"${self.max_drawdown:.2f} ({self.max_drawdown_pct:.1f}%)",
            "start_balance": f"${self.start_balance:.2f}",
            "end_balance": f"${self.end_balance:.2f}",
            "total_return": f"{self.total_return_pct:.2f}%",
            "signals_generated": self.num_signals,
            "signals_rejected": self.num_rejected,
            "rejection_rate": f"{self.rejection_rate:.1f}%",
        }


class BacktestEngine:
    """
    Backtest engine for historical data analysis
    
    Features:
    - Run strategy on historical candles
    - Calculate metrics (win rate, sharpe, drawdown)
    - Generate trade-by-trade report
    - Validate strategy logic
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize backtest engine"""
        self._lock = threading.RLock()
        
        self.config = config or {}
        self.initial_balance = Decimal(str(self.config.get('initial_balance', 10000)))
        self.commission = Decimal(str(self.config.get('commission', 0.001)))  # 0.1%
        
        logger.info(
            f"BacktestEngine initialized | Initial capital: ${self.initial_balance} | "
            f"Commission: {self.commission}"
        )
    
    def run_backtest(
        self,
        strategy_instance: Any,  # VGCryptoStrategy or similar
        data: pd.DataFrame,
        symbol: str = "BTC_USD"
    ) -> BacktestMetrics:
        """
        Run backtest on historical data
        
        Args:
            strategy_instance: Strategy object with calculate_indicators, generate_signal
            data: DataFrame with OHLCV data (columns: open, high, low, close, volume)
            symbol: Trading symbol
        
        Returns:
            BacktestMetrics with results
        """
        with self._lock:
            try:
                logger.info(f"Starting backtest for {symbol} | {len(data)} candles")
                
                metrics = BacktestMetrics()
                metrics.start_balance = float(self.initial_balance)
                
                current_balance = self.initial_balance
                drawdown_values = [float(self.initial_balance)]
                
                # Trade tracking
                current_trade: Optional[Dict[str, Any]] = None
                entry_candle = 0
                
                # Process each candle
                for idx in range(len(data)):
                    candle = data.iloc[idx]
                    close_price = Decimal(str(candle['close']))
                    
                    # Calculate indicators
                    window_data = data.iloc[:idx+1]
                    indicators_df = strategy_instance.calculate_indicators(window_data)
                    
                    # Check if in trade
                    if current_trade is None:
                        # Not in trade - check for BUY/SELL signal
                        signal = strategy_instance.generate_signal(indicators_df)
                        metrics.num_signals += 1
                        
                        if signal in ['BUY', 'SELL']:
                            # Calculate position size
                            position_size = float(current_balance) * 0.05 / float(close_price)  # 5% of balance
                            
                            # Open trade
                            current_trade = {
                                'symbol': symbol,
                                'direction': signal,
                                'entry_price': float(close_price),
                                'position_size': position_size,
                                'entry_candle': idx,
                                'entry_balance': float(current_balance),
                            }
                            
                            logger.debug(f"[{idx}] {symbol} {signal} @ {close_price}")
                    
                    else:
                        # In trade - check for exit
                        candles_held = idx - entry_candle
                        
                        # Check exit conditions
                        exit_signal = strategy_instance.manage_trade(indicators_df)
                        
                        if exit_signal == 'EXIT' or candles_held >= 50:  # Max hold 50 candles
                            # Close trade
                            exit_price = float(close_price)
                            
                            # Calculate P&L
                            if current_trade['direction'] == 'BUY':
                                pnl = (exit_price - current_trade['entry_price']) * current_trade['position_size']
                            else:  # SELL
                                pnl = (current_trade['entry_price'] - exit_price) * current_trade['position_size']
                            
                            # Apply commission
                            commission_cost = float(self.commission) * current_trade['position_size'] * exit_price
                            pnl -= commission_cost
                            
                            # Update balance
                            current_balance += Decimal(str(pnl))
                            
                            # Record trade
                            trade_record = {
                                **current_trade,
                                'exit_price': exit_price,
                                'exit_candle': idx,
                                'pnl': pnl,
                                'pnl_pct': (pnl / (current_trade['entry_price'] * current_trade['position_size']) * 100) 
                                          if (current_trade['entry_price'] * current_trade['position_size']) > 0 else 0,
                                'candles_held': candles_held,
                            }
                            
                            metrics.trades.append(trade_record)
                            metrics.total_trades += 1
                            
                            if pnl > 0:
                                metrics.winning_trades += 1
                                metrics.total_pnl += pnl
                                metrics.max_win = max(metrics.max_win, pnl)
                            else:
                                metrics.losing_trades += 1
                                metrics.total_pnl += pnl
                                metrics.max_loss = min(metrics.max_loss, pnl)
                            
                            logger.debug(
                                f"[{idx}] {symbol} EXIT {current_trade['direction']} @ {exit_price} | "
                                f"PnL: ${pnl:.2f} ({trade_record['pnl_pct']:.2f}%)"
                            )
                            
                            current_trade = None
                            entry_candle = 0
                    
                    # Track drawdown
                    drawdown_values.append(float(current_balance))
                
                # Close any remaining trade at end
                if current_trade is not None:
                    exit_price = float(data.iloc[-1]['close'])
                    if current_trade['direction'] == 'BUY':
                        pnl = (exit_price - current_trade['entry_price']) * current_trade['position_size']
                    else:
                        pnl = (current_trade['entry_price'] - exit_price) * current_trade['position_size']
                    
                    current_balance += Decimal(str(pnl))
                    metrics.total_trades += 1
                    if pnl > 0:
                        metrics.winning_trades += 1
                    else:
                        metrics.losing_trades += 1
                    metrics.total_pnl += pnl
                
                # Calculate final metrics
                metrics.end_balance = float(current_balance)
                metrics.total_return_pct = ((float(current_balance) - float(self.initial_balance)) / 
                                           float(self.initial_balance) * 100)
                
                if metrics.total_trades > 0:
                    metrics.win_rate = (metrics.winning_trades / metrics.total_trades * 100)
                    metrics.avg_pnl_per_trade = metrics.total_pnl / metrics.total_trades
                    metrics.expectancy = metrics.total_pnl / metrics.total_trades
                
                # Calculate max drawdown
                peak = max(drawdown_values)
                trough = min([v for v in drawdown_values if v <= peak])
                metrics.max_drawdown = peak - trough
                metrics.max_drawdown_pct = (metrics.max_drawdown / peak * 100) if peak > 0 else 0
                
                # Sharpe ratio (simplified - daily returns)
                if len(drawdown_values) > 1:
                    returns = np.diff(drawdown_values)
                    if np.std(returns) > 0:
                        metrics.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
                
                logger.info(
                    f"Backtest complete | Win rate: {metrics.win_rate:.1f}% | "
                    f"Total PnL: ${metrics.total_pnl:.2f} | Return: {metrics.total_return_pct:.2f}%"
                )
                
                return metrics
                
            except Exception as e:
                logger.error(f"Backtest error: {e}", exc_info=True)
                return BacktestMetrics()  # Return empty metrics


__all__ = ["BacktestEngine", "BacktestMetrics"]
