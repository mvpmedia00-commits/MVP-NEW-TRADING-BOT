# Trading Bot API

FastAPI-based RESTful API for managing and monitoring the trading bot.

## Features

- **Authentication**: API key-based authentication
- **CORS**: Configurable CORS middleware
- **Error Handling**: Comprehensive error handling with detailed responses
- **Documentation**: Auto-generated OpenAPI (Swagger) documentation
- **Type Safety**: Full type hints and Pydantic validation
- **Logging**: Structured logging for all operations

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the root directory:

```bash
# API Configuration
API_KEY=your-secret-api-key-change-this
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Environment
ENVIRONMENT=production
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
# From project root
python -m api.server

# Or with uvicorn directly
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### 4. Access Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## API Endpoints

### Health & Info

- `GET /` - API information
- `GET /health` - Health check

### Portfolio (`/api/v1/portfolio`)

- `GET /status` - Get portfolio status (equity, cash, P&L)
- `GET /positions` - Get all positions
- `GET /performance` - Get performance metrics

### Trades (`/api/v1/trades`)

- `GET /history` - Get trade history (paginated, filterable)
- `GET /active` - Get active/open trades
- `GET /{trade_id}` - Get specific trade details

### Strategies (`/api/v1/strategies`)

- `GET /list` - List all strategies
- `GET /{strategy_id}` - Get strategy details
- `POST /{strategy_id}/enable` - Enable a strategy
- `POST /{strategy_id}/disable` - Disable a strategy

### Bot Control (`/api/v1/control`)

- `POST /start` - Start the trading bot
- `POST /stop` - Stop the trading bot
- `GET /status` - Get bot status
- `POST /emergency-stop` - Emergency stop with position closure

## Authentication

All endpoints (except `/health` and `/`) require API key authentication.

Include the API key in the request header:

```bash
curl -H "X-API-Key: your-secret-api-key" http://localhost:8000/api/v1/portfolio/status
```

## Example Usage

### Get Portfolio Status

```bash
curl -X GET "http://localhost:8000/api/v1/portfolio/status" \
  -H "X-API-Key: your-secret-api-key"
```

Response:
```json
{
  "total_equity": 105247.50,
  "cash": 45000.00,
  "buying_power": 90000.00,
  "positions_value": 60247.50,
  "total_pnl": 5247.50,
  "total_pnl_percent": 5.24,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Get Trade History

```bash
curl -X GET "http://localhost:8000/api/v1/trades/history?page=1&page_size=10&symbol=AAPL" \
  -H "X-API-Key: your-secret-api-key"
```

### Start the Bot

```bash
curl -X POST "http://localhost:8000/api/v1/control/start" \
  -H "X-API-Key: your-secret-api-key"
```

Response:
```json
{
  "status": "running",
  "message": "Trading bot started successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Enable a Strategy

```bash
curl -X POST "http://localhost:8000/api/v1/strategies/momentum_1/enable" \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Market conditions favorable"}'
```

### Emergency Stop

```bash
curl -X POST "http://localhost:8000/api/v1/control/emergency-stop" \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "close_positions": true,
    "reason": "Market anomaly detected"
  }'
```

## Error Responses

All errors follow a standard format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": [
    {
      "field": "field_name",
      "message": "Field-specific error",
      "code": "error_code"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

- `401` - Invalid API key
- `404` - Resource not found
- `409` - Conflict (e.g., bot already running)
- `422` - Validation error
- `500` - Internal server error

## Development

### Project Structure

```
api/
├── __init__.py           # Package initialization
├── server.py             # Main FastAPI application
├── models/
│   ├── __init__.py
│   └── schemas.py        # Pydantic models
└── routes/
    ├── __init__.py
    ├── portfolio.py      # Portfolio endpoints
    ├── trades.py         # Trade endpoints
    ├── strategies.py     # Strategy endpoints
    └── control.py        # Bot control endpoints
```

### Running in Development Mode

```bash
# Enable auto-reload
export API_RELOAD=true
python -m api.server
```

### Adding New Endpoints

1. Define Pydantic models in `api/models/schemas.py`
2. Create route handler in appropriate file under `api/routes/`
3. Import and include router in `api/server.py`

## Security Best Practices

1. **Always change the default API key** in production
2. Use environment variables for sensitive configuration
3. Enable HTTPS in production
4. Restrict CORS origins to trusted domains
5. Monitor API access logs
6. Implement rate limiting (recommended)
7. Use strong, unique API keys

## Production Deployment

### Using Gunicorn

```bash
gunicorn api.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Behind Nginx

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Monitoring

The API logs all requests, responses, and errors. Monitor these logs for:

- Authentication failures
- API errors
- Performance issues
- Unusual trading activity

## TODO / Integration Points

The current implementation includes placeholder data. To integrate with the actual trading bot:

1. Connect portfolio endpoints to real portfolio data
2. Connect trade endpoints to trade database
3. Connect strategy endpoints to strategy manager
4. Connect control endpoints to bot lifecycle management
5. Implement database persistence
6. Add WebSocket support for real-time updates
7. Add rate limiting
8. Add request/response caching where appropriate

## Support

For issues or questions, please refer to the main project documentation.
