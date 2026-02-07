"""
Broker module - handles connections to different exchanges and brokers
"""

from .base_broker import BaseBroker
from .binance_broker import BinanceBroker
from .coinbase_broker import CoinbaseBroker
from .gemini_broker import GeminiBroker
from .mt4_broker import MT4Broker
from .cryptocom_broker import CryptocomBroker

__all__ = [
    'BaseBroker',
    'BinanceBroker',
    'CoinbaseBroker',
    'GeminiBroker',
    'MT4Broker',
    'CryptocomBroker'
]


def get_broker_class(broker_name: str):
    """
    Get the broker class for a given broker name
    
    Args:
        broker_name: Name of the broker (e.g., 'binance', 'coinbase')
        
    Returns:
        Broker class
    """
    broker_map = {
        'binance': BinanceBroker,
        'binance_us': BinanceBroker,  # Same implementation
        'coinbase': CoinbaseBroker,
        'coinbasepro': CoinbaseBroker,
        'gemini': GeminiBroker,
        'mt4': MT4Broker,
        'metatrader4': MT4Broker,
        'cryptocom': CryptocomBroker,
        'crypto.com': CryptocomBroker,
    }
    
    return broker_map.get(broker_name.lower())
