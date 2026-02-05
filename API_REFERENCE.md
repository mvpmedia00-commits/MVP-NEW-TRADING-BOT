# API Reference - Trading Bot REST API

Complete REST API documentation for the MVP Trading Bot.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL & Endpoints](#base-url--endpoints)
4. [Common Responses](#common-responses)
5. [Portfolio Endpoints](#portfolio-endpoints)
6. [Trade Endpoints](#trade-endpoints)
7. [Strategy Endpoints](#strategy-endpoints)
8. [Control Endpoints](#control-endpoints)
9. [Error Handling](#error-handling)
10. [Code Examples](#code-examples)
11. [Rate Limiting](#rate-limiting)
12. [WebSocket API](#websocket-api)

---

## Overview

The Trading Bot API is a RESTful API built with FastAPI that provides programmatic access to manage and monitor your trading bot.

### Features

- Portfolio management and monitoring
- Trade history and active positions
- Strategy configuration and control
- Bot control (start/stop/status)
- Real-time updates via WebSocket
- Comprehensive error handling
- API key authentication

### API Version

Current version: **v1.0.0**

### Technology Stack

- **Framework:** FastAPI
- **Authentication:** API Key (Header-based)
- **Data Format:** JSON
- **Documentation:** OpenAPI 3.0 (Swagger/ReDoc)

---

## Authentication

### API Key Authentication

All API endpoints (except `/health` and `/`) require authentication via API key.

#### Header Format

```
X-API-Key: your-api-key-here
```

#### Configuration

Set your API key in `.env`:

```bash
API_KEY=your-secure-api-key-change-this
```

#### Example Request

```bash
curl -H "X-API-Key: your-api-key" \
     https://localhost:8000/api/v1/portfolio/status
```

```python
import requests

headers = {'X-API-Key': 'your-api-key'}
response = requests.get('http://localhost:8000/api/v1/portfolio/status', 
                       headers=headers)
```

```javascript
fetch('http://localhost:8000/api/v1/portfolio/status', {
  headers: {
    'X-API-Key': 'your-api-key'
  }
})
```

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for API keys
3. **Rotate keys regularly** (every 90 days)
4. **Use HTTPS** in production
5. **Implement IP whitelisting** if possible
6. **Monitor API usage** for unusual activity

---

## Base URL & Endpoints

### Development

```
http://localhost:8000
```

### Production

```
https://your-domain.com
```

### API Root

```
GET /
```

Returns API information.

**Response:**
```json
{
  "name": "Trading Bot API",
  "version": "1.0.0",
  "description": "RESTful API for managing and monitoring the trading bot",
  "documentation": "/docs",
  "health": "/health"
}
```

### Health Check

```
GET /health
```

Check API health status (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T12:30:00.000Z",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "broker": "healthy",
    "bot": "running"
  }
}
```

### Interactive Documentation

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

---

## Common Responses

### Success Response

All successful responses return appropriate HTTP status codes (200, 201, etc.) with JSON data.

### Error Response

All errors return this format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Request conflicts with current state |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## Portfolio Endpoints

### Get Portfolio Status

Get current portfolio status including equity, cash, and P&L.

```
GET /api/v1/portfolio/status
```

**Headers:**
```
X-API-Key: your-api-key
```

**Response:** `200 OK`
```json
{
  "total_equity": 105247.50,
  "cash": 45000.00,
  "buying_power": 90000.00,
  "positions_value": 60247.50,
  "total_pnl": 5247.50,
  "total_pnl_percent": 5.24,
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```bash
# cURL
curl -H "X-API-Key: your-key" \
     http://localhost:8000/api/v1/portfolio/status
```

```python
# Python
import requests

headers = {'X-API-Key': 'your-key'}
response = requests.get(
    'http://localhost:8000/api/v1/portfolio/status',
    headers=headers
)
portfolio = response.json()
print(f"Total Equity: ${portfolio['total_equity']}")
```

```javascript
// JavaScript
const response = await fetch('http://localhost:8000/api/v1/portfolio/status', {
  headers: { 'X-API-Key': 'your-key' }
});
const portfolio = await response.json();
console.log(`Total Equity: $${portfolio.total_equity}`);
```

---

### Get Portfolio Positions

Retrieve all current portfolio positions.

```
GET /api/v1/portfolio/positions
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Filter by specific symbol |

**Example Request:**
```
GET /api/v1/portfolio/positions?symbol=AAPL
```

**Response:** `200 OK`
```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 10.0,
      "average_price": 150.50,
      "current_price": 155.25,
      "market_value": 1552.50,
      "unrealized_pnl": 47.50,
      "unrealized_pnl_percent": 3.16,
      "side": "BUY"
    },
    {
      "symbol": "GOOGL",
      "quantity": 5.0,
      "average_price": 2800.00,
      "current_price": 2850.50,
      "market_value": 14252.50,
      "unrealized_pnl": 252.50,
      "unrealized_pnl_percent": 1.80,
      "side": "BUY"
    }
  ],
  "total_positions": 2,
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```python
# Get all positions
response = requests.get(
    'http://localhost:8000/api/v1/portfolio/positions',
    headers={'X-API-Key': 'your-key'}
)
positions = response.json()

# Get positions for specific symbol
response = requests.get(
    'http://localhost:8000/api/v1/portfolio/positions',
    params={'symbol': 'AAPL'},
    headers={'X-API-Key': 'your-key'}
)
```

---

### Get Portfolio Performance

Retrieve portfolio performance metrics and statistics.

```
GET /api/v1/portfolio/performance
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| period | string | No | Time period (day, week, month, year, all) |

**Response:** `200 OK`
```json
{
  "total_return": 5.24,
  "daily_return": 0.15,
  "sharpe_ratio": 1.85,
  "max_drawdown": -2.34,
  "win_rate": 62.5,
  "total_trades": 48,
  "winning_trades": 30,
  "losing_trades": 18,
  "average_win": 125.50,
  "average_loss": -75.25,
  "profit_factor": 1.67,
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```python
# Get performance for last month
response = requests.get(
    'http://localhost:8000/api/v1/portfolio/performance',
    params={'period': 'month'},
    headers={'X-API-Key': 'your-key'}
)
metrics = response.json()
print(f"Total Return: {metrics['total_return']}%")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']}")
print(f"Win Rate: {metrics['win_rate']}%")
```

---

## Trade Endpoints

### Get Trade History

Retrieve historical trades with pagination and filtering.

```
GET /api/v1/trades/history
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number (≥1) |
| page_size | integer | No | 50 | Trades per page (1-100) |
| symbol | string | No | - | Filter by symbol |
| strategy | string | No | - | Filter by strategy |
| start_date | datetime | No | - | Filter by start date |
| end_date | datetime | No | - | Filter by end date |

**Example Request:**
```
GET /api/v1/trades/history?page=1&page_size=20&symbol=AAPL
```

**Response:** `200 OK`
```json
{
  "trades": [
    {
      "trade_id": "trade_1001",
      "symbol": "AAPL",
      "side": "BUY",
      "quantity": 10.0,
      "price": 150.50,
      "status": "FILLED",
      "strategy": "momentum_strategy",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "commission": 1.50,
      "pnl": 25.50
    },
    {
      "trade_id": "trade_1002",
      "symbol": "AAPL",
      "side": "SELL",
      "quantity": 10.0,
      "price": 153.05,
      "status": "FILLED",
      "strategy": "momentum_strategy",
      "timestamp": "2024-01-15T14:45:00.000Z",
      "commission": 1.53,
      "pnl": 25.50
    }
  ],
  "total_trades": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**Example:**

```python
# Get recent trades
response = requests.get(
    'http://localhost:8000/api/v1/trades/history',
    params={
        'page': 1,
        'page_size': 50,
        'symbol': 'AAPL'
    },
    headers={'X-API-Key': 'your-key'}
)
history = response.json()

# Get trades for date range
from datetime import datetime, timedelta

end_date = datetime.utcnow()
start_date = end_date - timedelta(days=30)

response = requests.get(
    'http://localhost:8000/api/v1/trades/history',
    params={
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'strategy': 'momentum_strategy'
    },
    headers={'X-API-Key': 'your-key'}
)
```

---

### Get Active Trades

Retrieve all currently active/open trades.

```
GET /api/v1/trades/active
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Filter by symbol |

**Response:** `200 OK`
```json
{
  "trades": [
    {
      "trade_id": "trade_5001",
      "symbol": "AAPL",
      "side": "BUY",
      "quantity": 10.0,
      "price": 155.25,
      "status": "OPEN",
      "strategy": "momentum_strategy",
      "timestamp": "2024-01-15T12:00:00.000Z",
      "commission": null,
      "pnl": null
    }
  ],
  "total_active": 1,
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```python
response = requests.get(
    'http://localhost:8000/api/v1/trades/active',
    headers={'X-API-Key': 'your-key'}
)
active_trades = response.json()
print(f"Active Trades: {active_trades['total_active']}")
```

---

### Get Trade by ID

Retrieve details for a specific trade.

```
GET /api/v1/trades/{trade_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| trade_id | string | Yes | Unique trade identifier |

**Example Request:**
```
GET /api/v1/trades/trade_1001
```

**Response:** `200 OK`
```json
{
  "trade_id": "trade_1001",
  "symbol": "AAPL",
  "side": "BUY",
  "quantity": 10.0,
  "price": 150.50,
  "status": "FILLED",
  "strategy": "momentum_strategy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "commission": 1.50,
  "pnl": 47.50
}
```

**Error Response:** `404 Not Found`
```json
{
  "error": "HTTPException",
  "message": "Trade trade_999 not found",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```python
trade_id = "trade_1001"
response = requests.get(
    f'http://localhost:8000/api/v1/trades/{trade_id}',
    headers={'X-API-Key': 'your-key'}
)

if response.status_code == 200:
    trade = response.json()
    print(f"Trade: {trade['symbol']} {trade['side']} {trade['quantity']}")
else:
    print(f"Error: {response.json()['message']}")
```

---

## Strategy Endpoints

### List All Strategies

Retrieve list of all available trading strategies.

```
GET /api/v1/strategies/list
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| enabled_only | boolean | No | Return only enabled strategies |

**Response:** `200 OK`
```json
{
  "strategies": [
    {
      "strategy_id": "momentum_1",
      "name": "Momentum Strategy",
      "description": "Trades based on price momentum indicators",
      "enabled": true,
      "parameters": {
        "lookback_period": 20,
        "threshold": 0.02,
        "symbols": ["AAPL", "GOOGL", "MSFT"]
      },
      "performance": {
        "total_return": 8.5,
        "win_rate": 65.0,
        "sharpe_ratio": 1.8
      }
    },
    {
      "strategy_id": "mean_reversion_1",
      "name": "Mean Reversion Strategy",
      "description": "Trades when price deviates from mean",
      "enabled": true,
      "parameters": {
        "window": 50,
        "std_dev": 2.0,
        "symbols": ["SPY", "QQQ"]
      },
      "performance": {
        "total_return": 5.2,
        "win_rate": 58.5,
        "sharpe_ratio": 1.4
      }
    }
  ],
  "total_strategies": 2,
  "active_strategies": 2
}
```

**Example:**

```python
# Get all strategies
response = requests.get(
    'http://localhost:8000/api/v1/strategies/list',
    headers={'X-API-Key': 'your-key'}
)
strategies = response.json()

# Get only enabled strategies
response = requests.get(
    'http://localhost:8000/api/v1/strategies/list',
    params={'enabled_only': True},
    headers={'X-API-Key': 'your-key'}
)
```

---

### Get Strategy Details

Retrieve detailed information about a specific strategy.

```
GET /api/v1/strategies/{strategy_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| strategy_id | string | Yes | Unique strategy identifier |

**Response:** `200 OK`
```json
{
  "strategy_id": "momentum_1",
  "name": "Momentum Strategy",
  "description": "Trades based on price momentum indicators",
  "enabled": true,
  "parameters": {
    "lookback_period": 20,
    "threshold": 0.02,
    "symbols": ["AAPL", "GOOGL", "MSFT"]
  },
  "performance": {
    "total_return": 8.5,
    "win_rate": 65.0,
    "sharpe_ratio": 1.8
  }
}
```

---

### Enable Strategy

Enable a trading strategy.

```
POST /api/v1/strategies/{strategy_id}/enable
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| strategy_id | string | Yes | Unique strategy identifier |

**Request Body (Optional):**
```json
{
  "reason": "Enabling after successful backtest"
}
```

**Response:** `200 OK`
```json
{
  "strategy_id": "momentum_1",
  "action": "enable",
  "success": true,
  "message": "Strategy momentum_1 enabled successfully",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```python
response = requests.post(
    'http://localhost:8000/api/v1/strategies/momentum_1/enable',
    json={'reason': 'Enabling after optimization'},
    headers={'X-API-Key': 'your-key'}
)
result = response.json()
print(result['message'])
```

---

### Disable Strategy

Disable a trading strategy.

```
POST /api/v1/strategies/{strategy_id}/disable
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| strategy_id | string | Yes | Unique strategy identifier |

**Request Body (Optional):**
```json
{
  "reason": "Poor performance in current market conditions"
}
```

**Response:** `200 OK`
```json
{
  "strategy_id": "momentum_1",
  "action": "disable",
  "success": true,
  "message": "Strategy momentum_1 disabled successfully",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

---

## Control Endpoints

### Start Bot

Start the trading bot.

```
POST /api/v1/control/start
```

**Response:** `200 OK`
```json
{
  "status": "RUNNING",
  "message": "Trading bot started successfully",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Error Response:** `409 Conflict` (if already running)
```json
{
  "error": "HTTPException",
  "message": "Bot is already running",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```python
response = requests.post(
    'http://localhost:8000/api/v1/control/start',
    headers={'X-API-Key': 'your-key'}
)

if response.status_code == 200:
    result = response.json()
    print(f"Bot status: {result['status']}")
elif response.status_code == 409:
    print("Bot is already running")
```

---

### Stop Bot

Stop the trading bot gracefully.

```
POST /api/v1/control/stop
```

**Response:** `200 OK`
```json
{
  "status": "STOPPED",
  "message": "Trading bot stopped successfully",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Error Response:** `409 Conflict` (if not running)
```json
{
  "error": "HTTPException",
  "message": "Bot is not running",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

---

### Get Bot Status

Get current status and statistics of the trading bot.

```
GET /api/v1/control/status
```

**Response:** `200 OK`
```json
{
  "status": "RUNNING",
  "uptime": 3600,
  "active_strategies": 2,
  "active_positions": 3,
  "last_trade": "2024-01-15T12:00:00.000Z",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Status Values:**
- `RUNNING` - Bot is actively trading
- `STOPPED` - Bot is stopped
- `PAUSED` - Bot is paused
- `ERROR` - Bot encountered an error

**Example:**

```python
response = requests.get(
    'http://localhost:8000/api/v1/control/status',
    headers={'X-API-Key': 'your-key'}
)
status = response.json()

print(f"Status: {status['status']}")
print(f"Uptime: {status['uptime']} seconds")
print(f"Active Strategies: {status['active_strategies']}")
print(f"Active Positions: {status['active_positions']}")
```

---

### Emergency Stop

Immediately stop the bot and optionally close all positions.

```
POST /api/v1/control/emergency-stop
```

**Request Body:**
```json
{
  "close_positions": true,
  "reason": "Market anomaly detected"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "positions_closed": 3,
  "message": "Emergency stop executed successfully. Reason: Market anomaly detected",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

**Example:**

```python
response = requests.post(
    'http://localhost:8000/api/v1/control/emergency-stop',
    json={
        'close_positions': True,
        'reason': 'Unusual market volatility'
    },
    headers={'X-API-Key': 'your-key'}
)

result = response.json()
print(f"Positions closed: {result['positions_closed']}")
print(f"Message: {result['message']}")
```

---

## Error Handling

### Error Response Format

All errors return this standardized format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

### Validation Errors

For validation errors (422), additional details are provided:

```json
{
  "error": "ValidationError",
  "message": "Invalid request parameters",
  "details": [
    {
      "field": "page_size",
      "message": "ensure this value is less than or equal to 100",
      "code": "value_error.number.not_le"
    }
  ],
  "timestamp": "2024-01-15T12:30:00.000Z"
}
```

### Error Handling Example

```python
import requests

def make_api_request(endpoint, **kwargs):
    """Make API request with error handling"""
    try:
        response = requests.get(
            f'http://localhost:8000{endpoint}',
            headers={'X-API-Key': 'your-key'},
            **kwargs
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Error: Invalid API key")
        elif e.response.status_code == 404:
            print("Error: Resource not found")
        elif e.response.status_code == 422:
            error = e.response.json()
            print(f"Validation Error: {error['message']}")
            for detail in error.get('details', []):
                print(f"  - {detail['field']}: {detail['message']}")
        else:
            error = e.response.json()
            print(f"Error: {error.get('message', 'Unknown error')}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage
portfolio = make_api_request('/api/v1/portfolio/status')
if portfolio:
    print(f"Equity: ${portfolio['total_equity']}")
```

---

## Code Examples

### Python Complete Example

```python
import requests
from datetime import datetime, timedelta

class TradingBotAPI:
    """Trading Bot API Client"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}
    
    def _request(self, method: str, endpoint: str, **kwargs):
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # Portfolio
    def get_portfolio_status(self):
        return self._request('GET', '/api/v1/portfolio/status')
    
    def get_positions(self, symbol=None):
        params = {'symbol': symbol} if symbol else {}
        return self._request('GET', '/api/v1/portfolio/positions', params=params)
    
    def get_performance(self, period='all'):
        return self._request('GET', '/api/v1/portfolio/performance', 
                           params={'period': period})
    
    # Trades
    def get_trade_history(self, page=1, page_size=50, **filters):
        params = {'page': page, 'page_size': page_size, **filters}
        return self._request('GET', '/api/v1/trades/history', params=params)
    
    def get_active_trades(self, symbol=None):
        params = {'symbol': symbol} if symbol else {}
        return self._request('GET', '/api/v1/trades/active', params=params)
    
    def get_trade(self, trade_id):
        return self._request('GET', f'/api/v1/trades/{trade_id}')
    
    # Strategies
    def list_strategies(self, enabled_only=None):
        params = {'enabled_only': enabled_only} if enabled_only is not None else {}
        return self._request('GET', '/api/v1/strategies/list', params=params)
    
    def get_strategy(self, strategy_id):
        return self._request('GET', f'/api/v1/strategies/{strategy_id}')
    
    def enable_strategy(self, strategy_id, reason=None):
        data = {'reason': reason} if reason else {}
        return self._request('POST', f'/api/v1/strategies/{strategy_id}/enable', 
                           json=data)
    
    def disable_strategy(self, strategy_id, reason=None):
        data = {'reason': reason} if reason else {}
        return self._request('POST', f'/api/v1/strategies/{strategy_id}/disable',
                           json=data)
    
    # Control
    def start_bot(self):
        return self._request('POST', '/api/v1/control/start')
    
    def stop_bot(self):
        return self._request('POST', '/api/v1/control/stop')
    
    def get_bot_status(self):
        return self._request('GET', '/api/v1/control/status')
    
    def emergency_stop(self, close_positions=True, reason=''):
        data = {'close_positions': close_positions, 'reason': reason}
        return self._request('POST', '/api/v1/control/emergency-stop', json=data)


# Usage Example
if __name__ == '__main__':
    api = TradingBotAPI('http://localhost:8000', 'your-api-key')
    
    # Get portfolio status
    portfolio = api.get_portfolio_status()
    print(f"Portfolio Equity: ${portfolio['total_equity']}")
    print(f"Total P&L: ${portfolio['total_pnl']} ({portfolio['total_pnl_percent']}%)")
    
    # Get active positions
    positions = api.get_positions()
    print(f"\nActive Positions: {positions['total_positions']}")
    for pos in positions['positions']:
        print(f"  {pos['symbol']}: {pos['quantity']} @ ${pos['current_price']}")
    
    # Get trade history
    history = api.get_trade_history(page=1, page_size=10, symbol='AAPL')
    print(f"\nRecent AAPL Trades: {len(history['trades'])}")
    
    # List strategies
    strategies = api.list_strategies(enabled_only=True)
    print(f"\nActive Strategies: {strategies['active_strategies']}")
    for strategy in strategies['strategies']:
        print(f"  {strategy['name']}: {strategy['performance']['total_return']}% return")
    
    # Get bot status
    status = api.get_bot_status()
    print(f"\nBot Status: {status['status']}")
    print(f"Uptime: {status['uptime']} seconds")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class TradingBotAPI {
  constructor(baseUrl, apiKey) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: { 'X-API-Key': apiKey }
    });
  }

  // Portfolio
  async getPortfolioStatus() {
    const { data } = await this.client.get('/api/v1/portfolio/status');
    return data;
  }

  async getPositions(symbol = null) {
    const { data } = await this.client.get('/api/v1/portfolio/positions', {
      params: symbol ? { symbol } : {}
    });
    return data;
  }

  async getPerformance(period = 'all') {
    const { data } = await this.client.get('/api/v1/portfolio/performance', {
      params: { period }
    });
    return data;
  }

  // Trades
  async getTradeHistory(params = {}) {
    const { data } = await this.client.get('/api/v1/trades/history', { params });
    return data;
  }

  async getActiveTrades(symbol = null) {
    const { data } = await this.client.get('/api/v1/trades/active', {
      params: symbol ? { symbol } : {}
    });
    return data;
  }

  // Strategies
  async listStrategies(enabledOnly = null) {
    const { data } = await this.client.get('/api/v1/strategies/list', {
      params: enabledOnly !== null ? { enabled_only: enabledOnly } : {}
    });
    return data;
  }

  async enableStrategy(strategyId, reason = null) {
    const { data } = await this.client.post(
      `/api/v1/strategies/${strategyId}/enable`,
      reason ? { reason } : {}
    );
    return data;
  }

  // Control
  async startBot() {
    const { data } = await this.client.post('/api/v1/control/start');
    return data;
  }

  async stopBot() {
    const { data } = await this.client.post('/api/v1/control/stop');
    return data;
  }

  async getBotStatus() {
    const { data } = await this.client.get('/api/v1/control/status');
    return data;
  }

  async emergencyStop(closePositions = true, reason = '') {
    const { data } = await this.client.post('/api/v1/control/emergency-stop', {
      close_positions: closePositions,
      reason
    });
    return data;
  }
}

// Usage
(async () => {
  const api = new TradingBotAPI('http://localhost:8000', 'your-api-key');
  
  try {
    // Get portfolio
    const portfolio = await api.getPortfolioStatus();
    console.log(`Portfolio Equity: $${portfolio.total_equity}`);
    
    // Get positions
    const positions = await api.getPositions();
    console.log(`Active Positions: ${positions.total_positions}`);
    
    // Get bot status
    const status = await api.getBotStatus();
    console.log(`Bot Status: ${status.status}`);
    
  } catch (error) {
    if (error.response) {
      console.error('API Error:', error.response.data.message);
    } else {
      console.error('Error:', error.message);
    }
  }
})();
```

---

## Rate Limiting

### Current Limits

- **Rate Limit:** Not currently enforced
- **Recommended:** Max 100 requests per minute
- **Burst:** Up to 10 requests per second

### Headers

Future implementation will include:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705327800
```

### Best Practices

1. **Implement exponential backoff** on errors
2. **Cache responses** when appropriate
3. **Use WebSocket** for real-time data
4. **Batch requests** when possible

---

## WebSocket API

### Coming Soon

Real-time updates via WebSocket for:

- Portfolio changes
- Trade executions
- Strategy signals
- Bot status updates

### Planned Endpoint

```
wss://localhost:8000/ws
```

### Planned Events

```json
{
  "event": "portfolio_update",
  "data": {
    "total_equity": 105500.00,
    "timestamp": "2024-01-15T12:30:00.000Z"
  }
}
```

```json
{
  "event": "trade_executed",
  "data": {
    "trade_id": "trade_1001",
    "symbol": "AAPL",
    "side": "BUY",
    "quantity": 10.0,
    "price": 150.50
  }
}
```

---

## Conclusion

This API reference covers all available endpoints. For additional help:

- **Interactive Docs:** Visit `/docs` for Swagger UI
- **Code Generation:** Use `/openapi.json` with code generators
- **Support:** Check [CONFIGURATION.md](CONFIGURATION.md) and [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md)

### Quick Links

- [Swagger UI](http://localhost:8000/docs) - Interactive API documentation
- [ReDoc](http://localhost:8000/redoc) - Alternative API documentation
- [Health Check](http://localhost:8000/health) - API health status

Happy trading! 🚀
