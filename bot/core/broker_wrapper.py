"""Broker wrapper with retry logic"""
import time
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BrokerWrapper:
    def __init__(self, broker, max_retries=3, retry_delay=2):
        self.broker = broker
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _retry_call(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed after {self.max_retries} attempts: {e}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                time.sleep(self.retry_delay * (attempt + 1))
    
    def create_order(self, symbol: str, order_type: str, side: str, amount: float, 
                    price: Optional[float] = None, params: Optional[Dict] = None):
        return self._retry_call(self.broker.create_order, symbol, order_type, side, amount, price, params)
    
    def get_ticker(self, symbol: str):
        return self._retry_call(self.broker.get_ticker, symbol)
    
    def get_balance(self):
        return self._retry_call(self.broker.get_balance)
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        return self._retry_call(self.broker.get_ohlcv, symbol, timeframe, limit)
    
    def cancel_order(self, order_id: str, symbol: str):
        return self._retry_call(self.broker.cancel_order, order_id, symbol)
    
    def get_order(self, order_id: str, symbol: str):
        return self._retry_call(self.broker.get_order, order_id, symbol)
    
    def __getattr__(self, name):
        return getattr(self.broker, name)
