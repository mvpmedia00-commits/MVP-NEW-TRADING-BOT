"""
Core components for the trading bot.

This package contains the essential components for portfolio management,
risk management, order execution, and data handling.
"""

from .portfolio import PortfolioManager
from .risk_manager import RiskManager
from .order_manager import OrderManager
from .data_manager import DataManager

__all__ = [
    'PortfolioManager',
    'RiskManager',
    'OrderManager',
    'DataManager',
]
