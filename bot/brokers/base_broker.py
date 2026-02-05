"""
Base broker interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseBroker(ABC):
    """
    Abstract base class for all broker implementations.
    All brokers must implement these methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the broker
        
        Args:
            config: Broker configuration dictionary
        """
        self.config = config
        self.name = config.get("name", "unknown")
        self.broker_type = config.get("type", "crypto")
        self.enabled = config.get("enabled", False)
        self.exchange = None  # Will be set by subclass
        
        logger.info(f"Initializing broker: {self.name}")
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the broker/exchange
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the broker/exchange"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balance
        
        Returns:
            Dictionary of currency balances
        """
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker/price for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Ticker information
        """
        pass
    
    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[List]:
        """
        Get OHLCV (candlestick) data
        
        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe (e.g., '1m', '5m', '1h', '1d')
            limit: Number of candles to retrieve
            
        Returns:
            List of OHLCV data
        """
        pass
    
    @abstractmethod
    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a new order
        
        Args:
            symbol: Trading pair symbol
            order_type: Order type ('market', 'limit', etc.)
            side: Order side ('buy' or 'sell')
            amount: Order amount
            price: Order price (for limit orders)
            params: Additional parameters
            
        Returns:
            Order information
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol
            
        Returns:
            Cancellation result
        """
        pass
    
    @abstractmethod
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get order status
        
        Args:
            order_id: Order ID
            symbol: Trading pair symbol
            
        Returns:
            Order information
        """
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders
        
        Args:
            symbol: Optional symbol to filter by
            
        Returns:
            List of open orders
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions
        
        Returns:
            List of open positions
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Check if broker is connected
        
        Returns:
            True if connected, False otherwise
        """
        return self.exchange is not None
    
    def get_supported_symbols(self) -> List[str]:
        """
        Get list of supported trading symbols
        
        Returns:
            List of supported symbols
        """
        return self.config.get("supported_pairs", [])
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if symbol is supported
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            True if supported, False otherwise
        """
        supported = self.get_supported_symbols()
        if not supported:  # If no list specified, assume all supported
            return True
        return symbol in supported
