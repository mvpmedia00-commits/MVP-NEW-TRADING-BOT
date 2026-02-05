"""
Trading Bot Package
"""

__version__ = '1.0.0'
__author__ = 'MVP Trading Bot Team'

from .utils import get_logger, ConfigLoader
from .brokers import BaseBroker, BinanceBroker, CoinbaseBroker, GeminiBroker, MT4Broker
from .strategies import BaseStrategy
from .core import Portfolio, RiskManager, OrderManager, DataManager

__all__ = [
    'get_logger',
    'ConfigLoader',
    'BaseBroker',
    'BinanceBroker',
    'CoinbaseBroker',
    'GeminiBroker',
    'MT4Broker',
    'BaseStrategy',
    'Portfolio',
    'RiskManager',
    'OrderManager',
    'DataManager',
]
