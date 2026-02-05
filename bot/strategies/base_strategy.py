"""
Base strategy class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import pandas as pd

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    All strategies must implement these methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.name = self.__class__.__name__
        self.parameters = config.get('parameters', {})
        self.risk_settings = config.get('risk_settings', {})
        self.enabled = config.get('enabled', True)
        
        # Position tracking
        self.position = None
        self.entry_price = None
        
        logger.info(f"Initialized strategy: {self.name}")
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate trading signal based on market data
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators needed for the strategy
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        pass
    
    def should_enter(self, data: pd.DataFrame) -> bool:
        """
        Check if should enter a position
        
        Args:
            data: DataFrame with OHLCV and indicators
            
        Returns:
            True if should enter, False otherwise
        """
        if self.position is not None:
            return False
        
        signal = self.generate_signal(data)
        return signal in ['BUY', 'SELL']
    
    def should_exit(self, data: pd.DataFrame, current_price: float) -> bool:
        """
        Check if should exit current position
        
        Args:
            data: DataFrame with OHLCV and indicators
            current_price: Current market price
            
        Returns:
            True if should exit, False otherwise
        """
        if self.position is None:
            return False
        
        # Check stop loss
        if self.check_stop_loss(current_price):
            logger.info(f"Stop loss triggered at {current_price}")
            return True
        
        # Check take profit
        if self.check_take_profit(current_price):
            logger.info(f"Take profit triggered at {current_price}")
            return True
        
        # Check strategy signal
        signal = self.generate_signal(data)
        if self.position == 'LONG' and signal == 'SELL':
            return True
        if self.position == 'SHORT' and signal == 'BUY':
            return True
        
        return False
    
    def check_stop_loss(self, current_price: float) -> bool:
        """
        Check if stop loss is triggered
        
        Args:
            current_price: Current market price
            
        Returns:
            True if stop loss triggered, False otherwise
        """
        if self.position is None or self.entry_price is None:
            return False
        
        stop_loss_pct = self.risk_settings.get('stop_loss_pct', 2.0) / 100
        
        if self.position == 'LONG':
            stop_loss_price = self.entry_price * (1 - stop_loss_pct)
            return current_price <= stop_loss_price
        elif self.position == 'SHORT':
            stop_loss_price = self.entry_price * (1 + stop_loss_pct)
            return current_price >= stop_loss_price
        
        return False
    
    def check_take_profit(self, current_price: float) -> bool:
        """
        Check if take profit is triggered
        
        Args:
            current_price: Current market price
            
        Returns:
            True if take profit triggered, False otherwise
        """
        if self.position is None or self.entry_price is None:
            return False
        
        take_profit_pct = self.risk_settings.get('take_profit_pct', 5.0) / 100
        
        if self.position == 'LONG':
            take_profit_price = self.entry_price * (1 + take_profit_pct)
            return current_price >= take_profit_price
        elif self.position == 'SHORT':
            take_profit_price = self.entry_price * (1 - take_profit_pct)
            return current_price <= take_profit_price
        
        return False
    
    def enter_position(self, position_type: str, entry_price: float):
        """
        Enter a position
        
        Args:
            position_type: 'LONG' or 'SHORT'
            entry_price: Entry price
        """
        self.position = position_type
        self.entry_price = entry_price
        logger.info(f"Entered {position_type} position at {entry_price}")
    
    def exit_position(self):
        """Exit current position"""
        if self.position:
            logger.info(f"Exited {self.position} position")
        self.position = None
        self.entry_price = None
    
    def get_position_size(self) -> float:
        """
        Calculate position size based on risk settings
        
        Returns:
            Position size
        """
        return self.risk_settings.get('position_size', 100)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current strategy status
        
        Returns:
            Dictionary with strategy status
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'position': self.position,
            'entry_price': self.entry_price,
            'parameters': self.parameters,
            'risk_settings': self.risk_settings
        }
