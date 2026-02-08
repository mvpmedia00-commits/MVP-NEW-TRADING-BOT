"""
Trading Strategies Package

Available strategies:
- SMACrossoverStrategy: Simple Moving Average Crossover
- RSIBBStrategy: RSI + Bollinger Bands
- MACDStrategy: MACD (Moving Average Convergence Divergence)
- EMAStrategy: Exponential Moving Average with multiple EMAs
- MPExtremeRangeStrategy: Market Probability Extreme Range (legacy - FX/Indices)
- MPCryptoStrategy: Market Probability Crypto Strategy (24/7, liquidity windows)
"""

from .base_strategy import BaseStrategy
from .sma_crossover import SMACrossoverStrategy
from .rsi_bb import RSIBBStrategy
from .macd_strategy import MACDStrategy
from .ema_strategy import EMAStrategy
from .mp_extreme_range import MPExtremeRangeStrategy
from .mp_crypto_strategy import MPCryptoStrategy
from .lgm_strategy import LGMStrategy

__all__ = [
    'BaseStrategy',
    'SMACrossoverStrategy',
    'RSIBBStrategy',
    'MACDStrategy',
    'EMAStrategy',
    'MPExtremeRangeStrategy',
    'MPCryptoStrategy',
    'LGMStrategy',
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
        'mp_extreme_range': MPExtremeRangeStrategy,
        'mp': MPExtremeRangeStrategy,
        'mp_eth': MPExtremeRangeStrategy,
        'mp_sol': MPExtremeRangeStrategy,
        # MP Crypto strategies (24/7, liquidity windows)
        'mp_crypto': MPCryptoStrategy,
        'mp_crypto_btc': MPCryptoStrategy,
        'mp_crypto_eth': MPCryptoStrategy,
        'mp_crypto_xrp': MPCryptoStrategy,
        'mp_crypto_doge': MPCryptoStrategy,
        'mp_crypto_shib': MPCryptoStrategy,
        'mp_crypto_trump': MPCryptoStrategy,
        # LGM strategy (rule-only)
        'lgm': LGMStrategy,
        'lgm_btc': LGMStrategy,
        'lgm_eth': LGMStrategy,
        'lgm_xrp': LGMStrategy,
        'lgm_doge': LGMStrategy,
        'lgm_shib': LGMStrategy,
        'lgm_trump': LGMStrategy,
    }
    
    return strategy_map.get(strategy_name.lower())

