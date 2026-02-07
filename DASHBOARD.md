# MVP Trading Bot Dashboard

A comprehensive web-based dashboard for monitoring and managing the MVP Trading Bot in real-time.

## Features

### Dashboard Components

- **Bot Status Panel**: Real-time bot status, operating mode, connected brokers, and active strategies
- **Portfolio Summary**: Current portfolio value, total P&L, win rate, open positions, and trade count
- **Market Data**: Live ticker prices and 24h change percentage for monitored symbols
- **Open Positions**: Detailed view of all open positions with unrealized P&L
- **Connected Brokers**: Status and balance information for all connected exchanges
- **Active Strategies**: List of running strategies and their configurations
- **Real-time Updates**: Auto-refresh every 5 seconds (configurable)

## Architecture

### Backend

**FastAPI API Server** (`api/server.py`)
- RESTful API endpoints on port 8000
- CORS enabled for cross-origin requests
- Static file serving for dashboard HTML/CSS/JS
- Exception handling and request logging
- Optional API key authentication for `/api/v1/*` endpoints

### API Endpoints

All dashboard endpoints are accessible at `http://YOUR_SERVER:8000/api/dashboard/`

```
GET /api/dashboard/bot-status       - Bot status and metrics
GET /api/dashboard/portfolio        - Portfolio balance and performance
GET /api/dashboard/brokers          - Connected brokers and balances
GET /api/dashboard/strategies       - Active strategies and parameters
GET /api/dashboard/market-data      - Live ticker data for symbols
GET /api/dashboard/positions        - Open positions with P&L
GET /api/dashboard/health           - Health check endpoint
```

### Frontend

**HTML5/CSS3/JavaScript Dashboard** (`api/static/index.html`)
- Responsive design (mobile-friendly)
- Real-time data updates via JavaScript Fetch API
- Professional color scheme and layout
- Auto-refresh with manual refresh controls
- Formatted currency and percentage displays

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Virtual environment set up (with all trading bot dependencies)
- Running trading bot instance

### 2. Install FastAPI (if not already installed)

```bash
pip install fastapi uvicorn python-multipart
```

### 3. Set Up Bot Instance Reference

The dashboard needs access to the trading bot instance. Update `api/dashboard_api.py`:

```python
from bot.main import TradingBot
from api import dashboard_api

# After bot initialization:
dashboard_api.set_bot_instance(bot_instance)
```

### 4. Start the Dashboard

**Option A: Using the startup script** (Recommended)
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

**Option B: Manual startup**

Terminal 1 - Start the trading bot:
```bash
python -m bot.main --paper-trading
```

Terminal 2 - Start the API server:
```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### 5. Access the Dashboard

Open your browser and navigate to:
```
http://YOUR_SERVER_IP:8000/dashboard
```

## Configuration

### Environment Variables

```bash
export API_HOST="0.0.0.0"          # API server host (default: 0.0.0.0)
export API_PORT="8000"             # API server port (default: 8000)
export API_KEY="your-secret-key"   # API authentication key (default: your-secret-api-key-change-this)
export CORS_ORIGINS="*"            # CORS allowed origins (default: *)
```

### Dashboard Settings

Edit `api/static/index.html` to customize:
- **Refresh interval**: Change `setInterval(refreshData, 5000)` (milliseconds)
- **Default symbols**: Update `fetch('/api/dashboard/market-data?symbols=BTC/USDT,ETH/USDT')`
- **Colors and styling**: Edit CSS in the `<style>` section

## Deployment on Oracle Cloud

### Prerequisites

- Oracle Cloud instance with Python 3.11 and virtual environment set up
- Trading bot deployed and running
- Port 8000 open in firewall

### 1. Enable Firewall Port

```bash
# Check current firewall rules
sudo firewall-cmd --list-all

# Add port 8000 (if using firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Or with iptables
sudo iptables -I INPUT -p tcp -m tcp --dport 8000 -j ACCEPT
```

### 2. Start Dashboard

```bash
# SSH into Oracle Cloud instance
ssh -i your_key.key ubuntu@YOUR_INSTANCE_IP

# Navigate to project directory
cd ~/MVP-NEW-TRADING-BOT

# Activate virtual environment
source venv/bin/activate

# Start dashboard
./start_dashboard.sh
```

### 3. Systemd Service Setup (For 24/7 Operation)

Create `/etc/systemd/system/trading-bot-dashboard.service`:

```ini
[Unit]
Description=MVP Trading Bot Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MVP-NEW-TRADING-BOT
Environment="PATH=/home/ubuntu/MVP-NEW-TRADING-BOT/venv/bin"
ExecStart=/usr/bin/python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable trading-bot-dashboard.service
sudo systemctl start trading-bot-dashboard.service

# Check status
sudo systemctl status trading-bot-dashboard.service

# View logs
sudo journalctl -f -u trading-bot-dashboard.service
```

## Performance Monitoring

### Memory Usage

The dashboard is lightweight and uses minimal resources:
- Base API server: ~50-100 MB
- Dashboard HTML/CSS/JS: ~30 KB
- Real-time update callbacks: ~1-5 MB per active connection

### API Response Times

Typical response times (milliseconds):
- Portfolio: 2-5 ms
- Brokers: 5-10 ms
- Market Data: 50-200 ms (depends on exchange API)
- Positions: 2-5 ms
- Strategies: 1-2 ms
- Bot Status: 1-3 ms

### Optimization Tips

1. **Reduce refresh interval** if data is stale:
   - Current: 5 seconds
   - Can go down to 2-3 seconds without server overload

2. **Cache market data** if hitting rate limits:
   - Modify `api/dashboard_api.py` to add Redis caching
   - Cache market data for 5-10 seconds

3. **Use reverse proxy** for production:
   - Set up Nginx/Apache to cache static files
   - Implement compression for API responses

## Troubleshooting

### Dashboard shows "Not Connected" or "Error"

1. Check if trading bot is running:
   ```bash
   ps aux | grep "bot.main"
   ```

2. Check if API server is running:
   ```bash
   ps aux | grep "uvicorn"
   ```

3. Check firewall settings:
   ```bash
   sudo firewall-cmd --list-all | grep 8000
   ```

4. Check API server logs:
   ```bash
   # If running in foreground, you'll see logs directly
   # If running as service:
   sudo journalctl -f -u trading-bot-dashboard.service
   ```

### API returns 500 error

1. Verify bot instance is properly connected:
   ```python
   # In Python REPL
   from bot.main import TradingBot
   from api import dashboard_api
   
   bot = TradingBot()
   bot.initialize()
   dashboard_api.set_bot_instance(bot)
   ```

2. Check if portfolio/brokers/strategies are initialized:
   - Bot should complete initialization step
   - Check logs for initialization errors

### Dashboard page doesn't load

1. Check if static files exist:
   ```bash
   ls -la api/static/
   ```

2. Check API server is accessible:
   ```bash
   curl http://localhost:8000/api/dashboard/health
   ```

3. Check browser console for JavaScript errors:
   - Press F12 in browser
   - Look for errors in Console tab

## Advanced Features

### Custom API Endpoints

You can add custom endpoints to the dashboard by modifying `api/dashboard_api.py`:

```python
@router.get("/api/dashboard/custom")
async def get_custom_data():
    """Your custom endpoint"""
    return {"success": True, "data": {...}}
```

Then update the HTML to fetch and display the new data.

### WebSocket Real-Time Updates

For ultra-low latency updates, implement WebSocket endpoints:

```python
from fastapi import WebSocket

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await get_bot_status()
        await websocket.send_json(data)
```

### Authentication

Enable API key authentication:

1. Update `.env` or environment variables:
   ```bash
   export API_KEY="your-super-secret-key"
   ```

2. API key is required for `/api/v1/*` endpoints
3. Dashboard endpoints are public (no auth required)
4. To add auth to dashboard: modify `api/server.py` to include dashboard routes in authenticated group

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│         Web Browser                             │
│  (HTML/CSS/JavaScript Dashboard)                │
└────────────────┬────────────────────────────────┘
                 │ HTTP/JSON
                 ↓
┌─────────────────────────────────────────────────┐
│         FastAPI Server (Port 8000)              │
│  ┌──────────────────────────────────────────┐  │
│  │  /api/dashboard/* Endpoints              │  │
│  │  • bot-status     (bot metrics)          │  │
│  │  • portfolio      (balances/P&L)         │  │
│  │  • brokers        (exchange status)      │  │
│  │  • strategies     (strategy config)      │  │
│  │  • market-data    (ticker prices)        │  │
│  │  • positions      (open trades)          │  │
│  │  • health         (health check)         │  │
│  └──────────────────────────────────────────┘  │
│  Static Files: /static/index.html               │
└────────────────┬────────────────────────────────┘
                 │ Python API
                 ↓
┌─────────────────────────────────────────────────┐
│      Trading Bot Instance (Main Process)        │
│  ┌──────────────────────────────────────────┐  │
│  │  • Portfolio Manager (balances/positions)│  │
│  │  • Broker Connections (CCXT)             │  │
│  │  • Strategy Engines (indicators)         │  │
│  │  • Risk Manager (position sizing)        │  │
│  │  • Order Manager (trade execution)       │  │
│  └──────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────┘
                 │ CCXT Library
                 ↓
        ┌────────────────┐
        │  Crypto.com    │
        │  Binance       │
        │  Coinbase Pro  │
        │  Gemini        │
        │  MetaTrader 4  │
        └────────────────┘
```

## API Reference

### GET /api/dashboard/bot-status

Returns aggregated bot metrics and status.

**Response:**
```json
{
  "success": true,
  "data": {
    "running": true,
    "mode": "paper-trading",
    "initialized": true,
    "connected_brokers": 1,
    "active_strategies": 2,
    "portfolio_value": 10500.50,
    "total_pnl": 500.50,
    "win_rate": 0.65,
    "open_positions": 3,
    "total_trades": 15
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### GET /api/dashboard/portfolio

Returns portfolio details with balances and performance metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "balances": {
      "USD": 5000.00,
      "BTC": 0.5,
      "ETH": 10.0
    },
    "performance": {
      "current_value": 10500.50,
      "total_pnl": 500.50,
      "win_rate": 0.65,
      "open_positions": 3,
      "total_trades": 15
    }
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### GET /api/dashboard/market-data?symbols=BTC/USDT,ETH/USDT

Fetches current ticker data for specified symbols.

**Parameters:**
- `symbols` (optional): Comma-separated symbol list (default: "BTC/USDT,ETH/USDT")

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC/USDT",
      "last": 42000.50,
      "bid": 42000.00,
      "ask": 42001.00,
      "high": 43000.00,
      "low": 41000.00,
      "change": 500.00,
      "changePercent": 1.20
    }
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

## Contributing

To add new dashboard features:

1. **Add API endpoint** in `api/dashboard_api.py`
2. **Update HTML** in `api/static/index.html` to fetch and display data
3. **Test locally** before deploying
4. **Update documentation** with new features

Example: Adding a new "Performance Chart" endpoint

```python
# api/dashboard_api.py
@router.get("/api/dashboard/performance-history")
async def get_performance_history(days: int = Query(7)):
    """Get portfolio performance history"""
    # Implementation
    pass
```

```javascript
// api/static/index.html
async function updatePerformanceChart() {
    const data = await fetchData('/performance-history?days=7');
    // Render chart
}
```

## Support

For issues or feature requests:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review bot logs: `bot.log`
3. Check API server logs: systemd journal
4. Open an issue on GitHub

## License

Same as MVP Trading Bot - See LICENSE file

---

**Last Updated**: January 2024  
**Version**: 1.0.0
