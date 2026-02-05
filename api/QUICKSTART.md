# Trading Bot API - Quick Reference

## Start Server

```bash
# Set API key (required for security)
export API_KEY="your-secure-api-key-here"

# Optional: Configure CORS
export CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"

# Start server
python -m api.server
```

Server will run on: http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Authentication

All API endpoints require API key in header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/portfolio/status
```

## Quick API Reference

### Portfolio
```bash
GET /api/v1/portfolio/status           # Portfolio overview
GET /api/v1/portfolio/positions        # All positions
GET /api/v1/portfolio/performance      # Performance metrics
```

### Trades
```bash
GET /api/v1/trades/history             # Trade history (paginated)
GET /api/v1/trades/active              # Active trades
GET /api/v1/trades/{trade_id}          # Specific trade
```

### Strategies
```bash
GET  /api/v1/strategies/list           # List all strategies
GET  /api/v1/strategies/{id}           # Strategy details
POST /api/v1/strategies/{id}/enable    # Enable strategy
POST /api/v1/strategies/{id}/disable   # Disable strategy
```

### Bot Control
```bash
POST /api/v1/control/start             # Start bot
POST /api/v1/control/stop              # Stop bot
GET  /api/v1/control/status            # Bot status
POST /api/v1/control/emergency-stop    # Emergency stop
```

## Python Client Example

```python
from api.example_client import TradingBotClient

# Initialize client
client = TradingBotClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Get portfolio status
portfolio = client.get_portfolio_status()
print(f"Equity: ${portfolio['total_equity']:,.2f}")

# Get positions
positions = client.get_positions()
for pos in positions['positions']:
    print(f"{pos['symbol']}: {pos['quantity']} @ ${pos['current_price']}")

# Start bot
response = client.start_bot()
print(response['message'])
```

## Testing

```bash
# Start server first
export API_KEY="test-api-key-12345"
python -m api.server

# In another terminal, run tests
python api/test_api.py
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn api.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker build -t trading-bot-api .
docker run -p 8000:8000 -e API_KEY="your-key" trading-bot-api
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| API_KEY | (required) | API authentication key |
| API_HOST | 0.0.0.0 | Server host |
| API_PORT | 8000 | Server port |
| API_RELOAD | false | Auto-reload on code changes |
| CORS_ORIGINS | * | Comma-separated allowed origins |
| ENVIRONMENT | development | Environment name |

## Security Checklist

- [ ] Change default API key
- [ ] Use HTTPS in production
- [ ] Restrict CORS origins
- [ ] Monitor API access logs
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting (recommended)

## Support Files

- `api/README.md` - Full documentation
- `api/test_api.py` - Test suite
- `api/example_client.py` - Python client library
- `api/server.py` - Main server implementation
