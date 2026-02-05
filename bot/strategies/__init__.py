"""
Trading Strategies Package

Available strategies:
- SMACrossoverStrategy: Simple Moving Average Crossover
- RSIBBStrategy: RSI + Bollinger Bands
- MACDStrategy: MACD (Moving Average Convergence Divergence)
- EMAStrategy: Exponential Moving Average with multiple EMAs
"""

from .base_strategy import BaseStrategy
from .sma_crossover import SMACrossoverStrategy
from .rsi_bb import RSIBBStrategy
from .macd_strategy import MACDStrategy
from .ema_strategy import EMAStrategy

__all__ = [
    'BaseStrategy',
    'SMACrossoverStrategy',
    'RSIBBStrategy',
    'MACDStrategy',
    'EMAStrategy',
]
