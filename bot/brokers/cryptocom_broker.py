"""
Crypto.com broker implementation
"""

import ccxt
from typing import Dict, List, Any, Optional

from .base_broker import BaseBroker
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CryptocomBroker(BaseBroker):
    """Crypto.com exchange broker implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Crypto.com broker
        
        Args:
            config: Broker configuration
        """
        super().__init__(config)
        self.exchange = None
    
    def connect(self) -> bool:
        """Connect to Crypto.com exchange"""
        try:
            credentials = self.config.get("api_credentials", {})
            settings = self.config.get("settings", {})
            
            # Initialize CCXT Crypto.com exchange
            exchange_params = {
                'apiKey': credentials.get('api_key'),
                'secret': credentials.get('api_secret'),
                'enableRateLimit': settings.get('enable_rate_limit', True),
                'timeout': settings.get('timeout', 30000),
            }
            
            # Use sandbox/testnet if configured
            if settings.get('testnet', True):
                self.exchange = ccxt.cryptocom(exchange_params)
                self.exchange.set_sandbox_mode(True)
                logger.info("Connected to Crypto.com sandbox")
            else:
                self.exchange = ccxt.cryptocom(exchange_params)
                logger.info("Connected to Crypto.com mainnet")
            
            # Load markets
            self.exchange.load_markets()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Crypto.com: {e}")
            self.exchange = None
            return False
    
    def disconnect(self):
        """Disconnect from Crypto.com"""
        if self.exchange:
            self.exchange.close()
            self.exchange = None
            logger.info("Disconnected from Crypto.com")
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            balance = self.exchange.fetch_balance()
            return {
                currency: {
                    'free': balance['free'].get(currency, 0),
                    'used': balance['used'].get(currency, 0),
                    'total': balance['total'].get(currency, 0)
                }
                for currency in balance['total']
                if balance['total'][currency] > 0
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker for symbol"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[List]:
        """Get OHLCV data"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise
    
    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new order"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            logger.info(f"Creating {side} {order_type} order for {amount} {symbol} at {price}")
            
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=params or {}
            )
            
            logger.info(f"Order created: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an order"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open orders"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            raise
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        if not self.exchange:
            raise ConnectionError("Not connected to Crypto.com")
        
        try:
            # For spot trading, positions are represented by non-zero balances
            balance = self.get_balance()
            positions = []
            
            for currency, amounts in balance.items():
                if amounts['total'] > 0:
                    positions.append({
                        'symbol': currency,
                        'amount': amounts['total'],
                        'free': amounts['free'],
                        'used': amounts['used']
                    })
            
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
