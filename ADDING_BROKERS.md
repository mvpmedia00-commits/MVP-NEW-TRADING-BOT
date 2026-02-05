# Adding New Brokers - Developer Guide

Complete guide for developers to integrate new brokers and exchanges into the MVP Trading Bot.

## Table of Contents

1. [Overview](#overview)
2. [BaseBroker Interface](#basebroker-interface)
3. [Implementation Guide](#implementation-guide)
4. [CCXT Integration](#ccxt-integration)
5. [Non-CCXT Implementation](#non-ccxt-implementation)
6. [Configuration Structure](#configuration-structure)
7. [Testing](#testing)
8. [Registration](#registration)
9. [Best Practices](#best-practices)
10. [Complete Examples](#complete-examples)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The trading bot uses a unified broker interface that allows easy integration of new exchanges and brokers. This guide walks you through the process of adding support for a new broker.

### Architecture

```
BaseBroker (Abstract Base Class)
    ↓
YourBroker (Your Implementation)
    ↓
CCXT or Custom API Client
    ↓
Exchange/Broker API
```

### Requirements

- Python 3.8+
- Understanding of the broker's API
- API documentation from the broker
- Test account or sandbox environment

### Integration Methods

1. **CCXT Integration** - For cryptocurrency exchanges supported by CCXT (recommended)
2. **Custom Integration** - For brokers not supported by CCXT or requiring custom logic

---

## BaseBroker Interface

All broker implementations must inherit from `BaseBroker` and implement required abstract methods.

### Source Code

Located at: `bot/brokers/base_broker.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseBroker(ABC):
    """Abstract base class for all broker implementations"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize broker with configuration"""
        self.config = config
        self.name = config.get("name", "unknown")
        self.broker_type = config.get("type", "crypto")
        self.enabled = config.get("enabled", False)
        self.exchange = None  # Will be set by subclass
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the broker/exchange"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the broker/exchange"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker/price for a symbol"""
        pass
    
    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
                   limit: int = 100) -> List[List]:
        """Get OHLCV (candlestick) data"""
        pass
    
    @abstractmethod
    def create_order(self, symbol: str, order_type: str, side: str,
                     amount: float, price: Optional[float] = None,
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open orders"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        pass
```

### Required Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `connect()` | Establish connection to broker | `bool` - Success status |
| `disconnect()` | Close connection | `None` |
| `get_balance()` | Retrieve account balance | `Dict[str, float]` |
| `get_ticker(symbol)` | Get current price data | `Dict[str, Any]` |
| `get_ohlcv(symbol, ...)` | Get candlestick data | `List[List]` |
| `create_order(...)` | Place a new order | `Dict[str, Any]` |
| `cancel_order(...)` | Cancel an order | `Dict[str, Any]` |
| `get_order(...)` | Get order details | `Dict[str, Any]` |
| `get_open_orders(...)` | List open orders | `List[Dict]` |
| `get_positions()` | Get open positions | `List[Dict]` |

### Optional Methods

These have default implementations but can be overridden:

```python
def is_connected(self) -> bool:
    """Check if broker is connected"""
    return self.exchange is not None

def get_supported_symbols(self) -> List[str]:
    """Get list of supported trading symbols"""
    return self.config.get("supported_pairs", [])

def validate_symbol(self, symbol: str) -> bool:
    """Validate if symbol is supported"""
    supported = self.get_supported_symbols()
    if not supported:
        return True
    return symbol in supported
```

---

## Implementation Guide

### Step 1: Create Broker File

Create a new file in `bot/brokers/` directory:

```bash
touch bot/brokers/your_broker.py
```

### Step 2: Implement Broker Class

```python
"""
Your Broker implementation
"""

import ccxt  # Or your custom API client
from typing import Dict, List, Any, Optional

from .base_broker import BaseBroker
from ..utils.logger import get_logger

logger = get_logger(__name__)


class YourBroker(BaseBroker):
    """Your broker implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize YourBroker"""
        super().__init__(config)
        self.exchange = None
        # Add broker-specific initialization
    
    def connect(self) -> bool:
        """Connect to YourBroker"""
        try:
            # Implementation here
            logger.info(f"Connected to {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from YourBroker"""
        if self.exchange:
            self.exchange.close()
            self.exchange = None
            logger.info(f"Disconnected from {self.name}")
    
    # Implement all other required methods...
```

### Step 3: Implement All Required Methods

See detailed implementations in the following sections.

### Step 4: Create Configuration Template

Create `config/brokers/your_broker.json`:

```json
{
  "name": "your_broker",
  "type": "crypto",
  "enabled": false,
  "description": "Your broker description",
  "api_credentials": {
    "api_key": "${YOUR_BROKER_API_KEY}",
    "api_secret": "${YOUR_BROKER_API_SECRET}"
  },
  "settings": {
    "testnet": true,
    "rate_limit": true,
    "timeout": 30000
  },
  "supported_pairs": [
    "BTC/USDT",
    "ETH/USDT"
  ]
}
```

### Step 5: Register Broker

Add import to `bot/brokers/__init__.py`:

```python
from .your_broker import YourBroker

__all__ = [
    'BaseBroker',
    'BinanceBroker',
    'CoinbaseBroker',
    'GeminiBroker',
    'YourBroker'  # Add your broker
]
```

### Step 6: Create Tests

Create `tests/test_your_broker.py`:

```python
import unittest
from bot.brokers.your_broker import YourBroker

class TestYourBroker(unittest.TestCase):
    def setUp(self):
        self.config = {
            "name": "your_broker",
            "api_credentials": {...}
        }
        self.broker = YourBroker(self.config)
    
    def test_connect(self):
        result = self.broker.connect()
        self.assertTrue(result)
    
    # Add more tests...
```

---

## CCXT Integration

For exchanges supported by CCXT (most cryptocurrency exchanges), use this approach.

### Check CCXT Support

```python
import ccxt

# List all supported exchanges
print(ccxt.exchanges)

# Check if your exchange is supported
if 'yourexchange' in ccxt.exchanges:
    print("Supported!")
```

### Implementation Template

```python
"""
CCXT-based broker implementation
"""

import ccxt
from typing import Dict, List, Any, Optional

from .base_broker import BaseBroker
from ..utils.logger import get_logger

logger = get_logger(__name__)


class YourCCXTBroker(BaseBroker):
    """Broker implementation using CCXT"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.exchange = None
    
    def connect(self) -> bool:
        """Connect to exchange via CCXT"""
        try:
            credentials = self.config.get("api_credentials", {})
            settings = self.config.get("settings", {})
            
            # Initialize CCXT exchange
            exchange_class = getattr(ccxt, self.name)
            
            exchange_params = {
                'apiKey': credentials.get('api_key'),
                'secret': credentials.get('api_secret'),
                'enableRateLimit': settings.get('enable_rate_limit', True),
                'timeout': settings.get('timeout', 30000),
            }
            
            # Add passphrase if required (e.g., Coinbase)
            if 'passphrase' in credentials:
                exchange_params['password'] = credentials['passphrase']
            
            # Initialize exchange
            self.exchange = exchange_class(exchange_params)
            
            # Use testnet/sandbox if configured
            if settings.get('testnet', False) or settings.get('sandbox', False):
                self.exchange.set_sandbox_mode(True)
                logger.info(f"Connected to {self.name} testnet")
            else:
                logger.info(f"Connected to {self.name} mainnet")
            
            # Load markets
            self.exchange.load_markets()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.name}: {e}")
            self.exchange = None
            return False
    
    def disconnect(self):
        """Disconnect from exchange"""
        if self.exchange:
            try:
                self.exchange.close()
            except:
                pass
            self.exchange = None
            logger.info(f"Disconnected from {self.name}")
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        if not self.exchange:
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            balance = self.exchange.fetch_balance()
            
            # Return formatted balance
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
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
                   limit: int = 100) -> List[List]:
        """Get OHLCV data"""
        if not self.exchange:
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise
    
    def create_order(self, symbol: str, order_type: str, side: str,
                     amount: float, price: Optional[float] = None,
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new order"""
        if not self.exchange:
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            params = params or {}
            
            # Create order based on type
            if order_type == 'market':
                order = self.exchange.create_market_order(
                    symbol, side, amount, params
                )
            elif order_type == 'limit':
                if price is None:
                    raise ValueError("Price required for limit orders")
                order = self.exchange.create_limit_order(
                    symbol, side, amount, price, params
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            logger.info(f"Created {order_type} {side} order for {symbol}: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        if not self.exchange:
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Cancelled order {order_id} for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        if not self.exchange:
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open orders"""
        if not self.exchange:
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            raise
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        if not self.exchange:
            raise ConnectionError(f"Not connected to {self.name}")
        
        try:
            # For spot trading, positions are derived from balance
            # For futures/margin, use fetch_positions if available
            if hasattr(self.exchange, 'fetch_positions'):
                positions = self.exchange.fetch_positions()
                return positions
            else:
                # Derive from balance for spot trading
                balance = self.get_balance()
                positions = []
                
                for currency, amounts in balance.items():
                    if amounts['total'] > 0:
                        positions.append({
                            'symbol': currency,
                            'amount': amounts['total'],
                            'side': 'long'
                        })
                
                return positions
                
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
```

### CCXT-Specific Features

#### Rate Limiting

```python
exchange_params = {
    'enableRateLimit': True,  # Enable automatic rate limiting
    'rateLimit': 1000,        # Milliseconds between requests
}
```

#### Sandbox Mode

```python
# Enable sandbox/testnet
self.exchange.set_sandbox_mode(True)

# Some exchanges use 'test' option
self.exchange = ccxt.binance({
    'apiKey': key,
    'secret': secret,
    'options': {'defaultType': 'future'},  # For testnet
})
```

#### Error Handling

```python
from ccxt import (
    NetworkError,
    ExchangeError,
    InvalidOrder,
    InsufficientFunds,
    RateLimitExceeded
)

try:
    order = self.exchange.create_order(...)
except RateLimitExceeded as e:
    logger.warning(f"Rate limit exceeded, retrying...")
    time.sleep(1)
    # Retry logic
except InsufficientFunds as e:
    logger.error(f"Insufficient funds: {e}")
    raise
except InvalidOrder as e:
    logger.error(f"Invalid order: {e}")
    raise
except NetworkError as e:
    logger.error(f"Network error: {e}")
    # Retry logic
```

---

## Non-CCXT Implementation

For brokers not supported by CCXT, implement using the broker's native API.

### Example: Custom REST API

```python
"""
Custom broker implementation using REST API
"""

import requests
import hmac
import hashlib
import time
from typing import Dict, List, Any, Optional

from .base_broker import BaseBroker
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CustomBroker(BaseBroker):
    """Custom broker using native REST API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        credentials = config.get("api_credentials", {})
        settings = config.get("settings", {})
        
        self.api_key = credentials.get('api_key')
        self.api_secret = credentials.get('api_secret')
        
        # API endpoints
        if settings.get('testnet', False):
            self.base_url = "https://testnet.api.yourbroker.com"
        else:
            self.base_url = "https://api.yourbroker.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate request signature"""
        # Implement broker-specific signature generation
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, 
                 params: Optional[Dict] = None,
                 signed: bool = False) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=params)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def connect(self) -> bool:
        """Test connection"""
        try:
            # Test with a simple API call
            response = self._request('GET', '/api/v1/time')
            logger.info(f"Connected to {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close connection"""
        if self.session:
            self.session.close()
            logger.info(f"Disconnected from {self.name}")
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            data = self._request('GET', '/api/v1/account', signed=True)
            
            # Parse response based on broker's format
            balances = {}
            for item in data.get('balances', []):
                currency = item['asset']
                balances[currency] = {
                    'free': float(item['free']),
                    'used': float(item['locked']),
                    'total': float(item['free']) + float(item['locked'])
                }
            
            return balances
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data"""
        try:
            params = {'symbol': symbol}
            data = self._request('GET', '/api/v1/ticker/24hr', params=params)
            
            # Normalize to standard format
            return {
                'symbol': data['symbol'],
                'last': float(data['lastPrice']),
                'bid': float(data['bidPrice']),
                'ask': float(data['askPrice']),
                'high': float(data['highPrice']),
                'low': float(data['lowPrice']),
                'volume': float(data['volume']),
                'timestamp': data['closeTime']
            }
            
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            raise
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h',
                   limit: int = 100) -> List[List]:
        """Get OHLCV data"""
        try:
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': limit
            }
            data = self._request('GET', '/api/v1/klines', params=params)
            
            # Convert to standard OHLCV format
            # [timestamp, open, high, low, close, volume]
            ohlcv = []
            for candle in data:
                ohlcv.append([
                    int(candle[0]),        # timestamp
                    float(candle[1]),      # open
                    float(candle[2]),      # high
                    float(candle[3]),      # low
                    float(candle[4]),      # close
                    float(candle[5])       # volume
                ])
            
            return ohlcv
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            raise
    
    def create_order(self, symbol: str, order_type: str, side: str,
                     amount: float, price: Optional[float] = None,
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Create order"""
        try:
            order_params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': amount
            }
            
            if order_type.lower() == 'limit':
                if price is None:
                    raise ValueError("Price required for limit orders")
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'
            
            # Add additional parameters
            if params:
                order_params.update(params)
            
            data = self._request('POST', '/api/v1/order', 
                               params=order_params, signed=True)
            
            logger.info(f"Created order: {data['orderId']}")
            return data
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel order"""
        try:
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            data = self._request('DELETE', '/api/v1/order',
                               params=params, signed=True)
            
            logger.info(f"Cancelled order: {order_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise
    
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        try:
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            data = self._request('GET', '/api/v1/order',
                               params=params, signed=True)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching order: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders"""
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            
            data = self._request('GET', '/api/v1/openOrders',
                               params=params, signed=True)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            raise
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions"""
        try:
            data = self._request('GET', '/api/v1/positions', signed=True)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
```

### WebSocket Support

For real-time data:

```python
import websocket
import json
import threading

class CustomBrokerWithWS(CustomBroker):
    """Broker with WebSocket support"""
    
    def __init__(self, config):
        super().__init__(config)
        self.ws = None
        self.ws_thread = None
        self.callbacks = {}
    
    def connect_websocket(self):
        """Connect to WebSocket"""
        ws_url = "wss://stream.yourbroker.com"
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def _on_message(self, ws, message):
        """Handle WebSocket message"""
        data = json.loads(message)
        
        # Call registered callbacks
        event_type = data.get('e')
        if event_type in self.callbacks:
            self.callbacks[event_type](data)
    
    def subscribe_ticker(self, symbol: str, callback):
        """Subscribe to ticker updates"""
        self.callbacks['ticker'] = callback
        
        # Send subscription message
        subscribe_msg = {
            'method': 'SUBSCRIBE',
            'params': [f"{symbol}@ticker"],
            'id': 1
        }
        self.ws.send(json.dumps(subscribe_msg))
```

---

## Configuration Structure

### Broker Configuration Template

`config/brokers/_template.json`:

```json
{
  "name": "TEMPLATE_BROKER",
  "type": "crypto",
  "enabled": false,
  "description": "Template configuration file for adding new brokers",
  
  "api_credentials": {
    "api_key": "${BROKER_API_KEY}",
    "api_secret": "${BROKER_API_SECRET}",
    "passphrase": "${BROKER_PASSPHRASE}",
    "additional_fields": {}
  },
  
  "settings": {
    "testnet": true,
    "rate_limit": true,
    "timeout": 30000,
    "enable_rate_limit": true,
    "recv_window": 5000
  },
  
  "supported_pairs": [
    "BTC/USDT",
    "ETH/USDT"
  ],
  
  "trading_settings": {
    "default_order_type": "limit",
    "default_time_in_force": "GTC",
    "enable_margin": false,
    "enable_futures": false,
    "slippage_tolerance": 0.001
  },
  
  "risk_management": {
    "max_position_size": 1000,
    "max_leverage": 1,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 5.0
  },
  
  "custom_settings": {
    "note": "Add any broker-specific settings here"
  }
}
```

### Environment Variables

Add to `.env.example`:

```bash
# Your Broker Configuration
YOUR_BROKER_API_KEY=
YOUR_BROKER_API_SECRET=
YOUR_BROKER_TESTNET=true
```

---

## Testing

### Unit Tests

Create `tests/test_your_broker.py`:

```python
import unittest
from unittest.mock import Mock, patch
from bot.brokers.your_broker import YourBroker


class TestYourBroker(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "name": "your_broker",
            "type": "crypto",
            "enabled": True,
            "api_credentials": {
                "api_key": "test_key",
                "api_secret": "test_secret"
            },
            "settings": {
                "testnet": True,
                "timeout": 30000
            }
        }
        self.broker = YourBroker(self.config)
    
    def test_initialization(self):
        """Test broker initialization"""
        self.assertEqual(self.broker.name, "your_broker")
        self.assertEqual(self.broker.broker_type, "crypto")
        self.assertTrue(self.broker.enabled)
    
    @patch('ccxt.yourbroker')
    def test_connect(self, mock_exchange):
        """Test connection"""
        mock_exchange.return_value.load_markets.return_value = {}
        
        result = self.broker.connect()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.broker.exchange)
    
    @patch('ccxt.yourbroker')
    def test_get_balance(self, mock_exchange):
        """Test balance retrieval"""
        mock_balance = {
            'free': {'BTC': 1.0, 'USDT': 1000.0},
            'used': {'BTC': 0.0, 'USDT': 0.0},
            'total': {'BTC': 1.0, 'USDT': 1000.0}
        }
        mock_exchange.return_value.fetch_balance.return_value = mock_balance
        
        self.broker.exchange = mock_exchange.return_value
        balance = self.broker.get_balance()
        
        self.assertIn('BTC', balance)
        self.assertEqual(balance['BTC']['total'], 1.0)
    
    @patch('ccxt.yourbroker')
    def test_get_ticker(self, mock_exchange):
        """Test ticker retrieval"""
        mock_ticker = {
            'symbol': 'BTC/USDT',
            'last': 50000.0,
            'bid': 49999.0,
            'ask': 50001.0
        }
        mock_exchange.return_value.fetch_ticker.return_value = mock_ticker
        
        self.broker.exchange = mock_exchange.return_value
        ticker = self.broker.get_ticker('BTC/USDT')
        
        self.assertEqual(ticker['symbol'], 'BTC/USDT')
        self.assertEqual(ticker['last'], 50000.0)
    
    @patch('ccxt.yourbroker')
    def test_create_order(self, mock_exchange):
        """Test order creation"""
        mock_order = {
            'id': '12345',
            'symbol': 'BTC/USDT',
            'type': 'limit',
            'side': 'buy',
            'amount': 0.1,
            'price': 50000.0
        }
        mock_exchange.return_value.create_limit_order.return_value = mock_order
        
        self.broker.exchange = mock_exchange.return_value
        order = self.broker.create_order('BTC/USDT', 'limit', 'buy', 0.1, 50000.0)
        
        self.assertEqual(order['id'], '12345')
        self.assertEqual(order['type'], 'limit')
    
    def tearDown(self):
        """Clean up after tests"""
        if self.broker.exchange:
            self.broker.disconnect()


if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
import os
from dotenv import load_dotenv

load_dotenv()


class TestYourBrokerIntegration(unittest.TestCase):
    """Integration tests with real API (testnet)"""
    
    @classmethod
    def setUpClass(cls):
        """Set up for integration tests"""
        cls.config = {
            "name": "your_broker",
            "api_credentials": {
                "api_key": os.getenv('YOUR_BROKER_API_KEY'),
                "api_secret": os.getenv('YOUR_BROKER_API_SECRET')
            },
            "settings": {"testnet": True}
        }
        cls.broker = YourBroker(cls.config)
        cls.broker.connect()
    
    def test_real_connection(self):
        """Test real connection to testnet"""
        self.assertTrue(self.broker.is_connected())
    
    def test_real_balance(self):
        """Test fetching real balance"""
        balance = self.broker.get_balance()
        self.assertIsInstance(balance, dict)
    
    def test_real_ticker(self):
        """Test fetching real ticker"""
        ticker = self.broker.get_ticker('BTC/USDT')
        self.assertIn('last', ticker)
        self.assertGreater(ticker['last'], 0)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.broker.disconnect()
```

### Manual Testing Script

```python
#!/usr/bin/env python3
"""
Manual test script for YourBroker
"""

import json
from bot.brokers.your_broker import YourBroker

def main():
    # Load configuration
    with open('config/brokers/your_broker.json') as f:
        config = json.load(f)
    
    # Initialize broker
    print("1. Initializing broker...")
    broker = YourBroker(config)
    
    # Connect
    print("2. Connecting...")
    if not broker.connect():
        print("❌ Connection failed")
        return
    print("✅ Connected")
    
    # Get balance
    print("\n3. Fetching balance...")
    balance = broker.get_balance()
    for currency, amounts in balance.items():
        if amounts['total'] > 0:
            print(f"   {currency}: {amounts['total']}")
    
    # Get ticker
    print("\n4. Fetching ticker...")
    ticker = broker.get_ticker('BTC/USDT')
    print(f"   BTC/USDT: ${ticker['last']}")
    
    # Get OHLCV
    print("\n5. Fetching OHLCV...")
    ohlcv = broker.get_ohlcv('BTC/USDT', '1h', 5)
    print(f"   Retrieved {len(ohlcv)} candles")
    print(f"   Latest close: ${ohlcv[-1][4]}")
    
    # Disconnect
    print("\n6. Disconnecting...")
    broker.disconnect()
    print("✅ Done")


if __name__ == '__main__':
    main()
```

---

## Registration

### Add to Broker Registry

Update `bot/brokers/__init__.py`:

```python
from .base_broker import BaseBroker
from .binance_broker import BinanceBroker
from .coinbase_broker import CoinbaseBroker
from .gemini_broker import GeminiBroker
from .your_broker import YourBroker  # Add import

__all__ = [
    'BaseBroker',
    'BinanceBroker',
    'CoinbaseBroker',
    'GeminiBroker',
    'YourBroker'  # Add to exports
]

# Broker registry for dynamic loading
BROKER_REGISTRY = {
    'binance': BinanceBroker,
    'coinbase': CoinbaseBroker,
    'gemini': GeminiBroker,
    'your_broker': YourBroker  # Add to registry
}
```

### Broker Factory

Create/update broker factory:

```python
from bot.brokers import BROKER_REGISTRY

def create_broker(broker_name: str, config: dict):
    """Factory function to create broker instances"""
    
    broker_class = BROKER_REGISTRY.get(broker_name)
    
    if not broker_class:
        raise ValueError(f"Unsupported broker: {broker_name}")
    
    return broker_class(config)
```

---

## Best Practices

### 1. Error Handling

```python
def get_balance(self) -> Dict[str, float]:
    """Get balance with proper error handling"""
    if not self.exchange:
        raise ConnectionError(f"Not connected to {self.name}")
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            balance = self.exchange.fetch_balance()
            return self._format_balance(balance)
            
        except NetworkError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Network error, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                raise
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
```

### 2. Logging

```python
from bot.utils.logger import get_logger

logger = get_logger(__name__)

# Log important events
logger.info(f"Connected to {self.name}")
logger.warning(f"Rate limit approaching")
logger.error(f"Failed to create order: {error}")
logger.debug(f"Raw API response: {response}")
```

### 3. Configuration Validation

```python
def __init__(self, config: Dict[str, Any]):
    super().__init__(config)
    
    # Validate required fields
    credentials = config.get("api_credentials", {})
    if not credentials.get('api_key'):
        raise ValueError("API key is required")
    if not credentials.get('api_secret'):
        raise ValueError("API secret is required")
    
    # Validate settings
    settings = config.get("settings", {})
    timeout = settings.get('timeout', 30000)
    if timeout < 1000:
        logger.warning(f"Timeout {timeout}ms is very low")
```

### 4. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    """Rate limiting decorator"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator

# Usage
@rate_limit(calls_per_second=2)
def create_order(self, ...):
    # Implementation
    pass
```

### 5. Data Normalization

```python
def _normalize_ticker(self, raw_ticker: Dict) -> Dict:
    """Normalize ticker to standard format"""
    return {
        'symbol': raw_ticker.get('symbol'),
        'last': float(raw_ticker.get('lastPrice', 0)),
        'bid': float(raw_ticker.get('bidPrice', 0)),
        'ask': float(raw_ticker.get('askPrice', 0)),
        'high': float(raw_ticker.get('highPrice', 0)),
        'low': float(raw_ticker.get('lowPrice', 0)),
        'volume': float(raw_ticker.get('volume', 0)),
        'timestamp': int(raw_ticker.get('closeTime', 0))
    }
```

### 6. Documentation

```python
def create_order(self, symbol: str, order_type: str, side: str,
                 amount: float, price: Optional[float] = None,
                 params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Create a new order.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        order_type: Order type ('market' or 'limit')
        side: Order side ('buy' or 'sell')
        amount: Order amount in base currency
        price: Order price (required for limit orders)
        params: Additional broker-specific parameters
    
    Returns:
        Order information dictionary containing:
        - id: Order ID
        - symbol: Trading pair
        - type: Order type
        - side: Order side
        - amount: Order amount
        - price: Order price
        - status: Order status
        - timestamp: Creation timestamp
    
    Raises:
        ConnectionError: If not connected to broker
        ValueError: If invalid parameters provided
        BrokerError: If order creation fails
    
    Example:
        >>> broker.create_order('BTC/USDT', 'limit', 'buy', 0.1, 50000.0)
        {'id': '12345', 'symbol': 'BTC/USDT', ...}
    """
    # Implementation
```

---

## Complete Examples

See the complete implementation examples in the previous sections:
1. CCXT-based broker (YourCCXTBroker)
2. Custom REST API broker (CustomBroker)
3. WebSocket-enabled broker (CustomBrokerWithWS)

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```python
# Ensure proper imports
from .base_broker import BaseBroker  # Relative import
from ..utils.logger import get_logger  # Go up one level
```

#### 2. Signature/Authentication Errors

```python
# Check signature generation
def _generate_signature(self, params):
    # Ensure proper sorting and encoding
    query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    
    # Use correct hash algorithm
    signature = hmac.new(
        self.api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256  # or sha512, depending on broker
    ).hexdigest()
    
    return signature
```

#### 3. Time Synchronization Issues

```python
import ntplib
from time import ctime

def check_time_sync(self):
    """Check if system time is synchronized"""
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        
        offset = response.offset
        if abs(offset) > 1000:  # More than 1 second off
            logger.warning(f"Time offset: {offset}ms")
            return False
        
        return True
    except:
        logger.warning("Could not check time sync")
        return True
```

#### 4. SSL Errors

```python
import certifi
import ssl

# Use certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())
```

---

## Conclusion

You now have everything needed to integrate a new broker:

1. Understand the BaseBroker interface
2. Choose CCXT or custom implementation
3. Implement all required methods
4. Create configuration files
5. Write comprehensive tests
6. Register the broker
7. Document the integration

**Next Steps:**
- Test thoroughly in sandbox/testnet
- Add to documentation
- Submit pull request (if contributing)
- Monitor in production

For help:
- See [BROKER_SETUP.md](BROKER_SETUP.md) for user setup guide
- See [API_REFERENCE.md](API_REFERENCE.md) for API documentation
- Review existing broker implementations for reference
