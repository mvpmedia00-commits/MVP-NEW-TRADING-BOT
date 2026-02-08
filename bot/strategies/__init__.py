"""
Trading Strategies Package

Available strategies:
- SMACrossoverStrategy: Simple Moving Average Crossover
- RSIBBStrategy: RSI + Bollinger Bands
- MACDStrategy: MACD (Moving Average Convergence Divergence)
- EMAStrategy: Exponential Moving Average with multiple EMAs
- VGExtremeRangeStrategy: Vector Games Extreme Range (legacy - FX/Indices)
- VGCryptoStrategy: Vector Games Crypto Strategy (24/7, liquidity windows)
"""

from .base_strategy import BaseStrategy
from .sma_crossover import SMACrossoverStrategy
from .rsi_bb import RSIBBStrategy
from .macd_strategy import MACDStrategy
from .ema_strategy import EMAStrategy
from .vg_extreme_range import VGExtremeRangeStrategy
from .vg_crypto_strategy import VGCryptoStrategy

__all__ = [
    'BaseStrategy',
    'SMACrossoverStrategy',
    'RSIBBStrategy',
    'MACDStrategy',
    'EMAStrategy',
    'VGExtremeRangeStrategy',
    'VGCryptoStrategy',
    'get_strategy_class',
]


def get_strategy_class(strategy_name: str):
    """
    Get the strategy class for a given strategy name
    
    Args:
        strategy_name: Name of the strategy (e.g., 'sma_crossover', 'vg_crypto')
        
    Returns:
        Strategy class
    """
    strategy_map = {
        'sma_crossover': SMACrossoverStrategy,
        'sma': SMACrossoverStrategy,
        'rsi_bb': RSIBBStrategy,
        'rsi_bollinger': RSIBBStrategy,
        'macd': MACDStrategy,
        'ema': EMAStrategy,
        'vg_extreme_range': VGExtremeRangeStrategy,
        'vg': VGExtremeRangeStrategy,
        'vg_eth': VGExtremeRangeStrategy,
        'vg_sol': VGExtremeRangeStrategy,
        # VG Crypto strategies (24/7, liquidity windows)
        'vg_crypto': VGCryptoStrategy,
        'vg_crypto_btc': VGCryptoStrategy,
        'vg_crypto_eth': VGCryptoStrategy,
        'vg_crypto_xrp': VGCryptoStrategy,
        'vg_crypto_doge': VGCryptoStrategy,
        'vg_crypto_shib': VGCryptoStrategy,
        'vg_crypto_trump': VGCryptoStrategy,
    }
    
    return strategy_map.get(strategy_name.lower())

