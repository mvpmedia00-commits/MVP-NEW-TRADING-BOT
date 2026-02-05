# Configuration Reference

Complete configuration reference for the MVP Trading Bot covering all settings and options.

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Global Configuration](#global-configuration)
4. [Broker Configuration](#broker-configuration)
5. [Strategy Configuration](#strategy-configuration)
6. [Risk Management Settings](#risk-management-settings)
7. [Logging Configuration](#logging-configuration)
8. [Database Configuration](#database-configuration)
9. [Redis Configuration](#redis-configuration)
10. [Docker Configuration](#docker-configuration)
11. [Configuration Validation](#configuration-validation)
12. [Common Scenarios](#common-scenarios)

---

## Overview

The trading bot uses a layered configuration approach:

1. **Environment Variables** (`.env`) - Secrets and environment-specific settings
2. **Global Config** (`config/global.json`) - Bot-wide settings
3. **Broker Configs** (`config/brokers/*.json`) - Broker-specific settings
4. **Strategy Configs** (`config/strategies/*.json`) - Strategy-specific settings

### Configuration Priority

```
Environment Variables > Global Config > Default Values
```

### File Locations

```
/home/runner/work/MVP-NEW-TRADING-BOT/MVP-NEW-TRADING-BOT/
├── .env                              # Environment variables (NEVER commit!)
├── .env.example                      # Environment variables template
├── config/
│   ├── global.json                   # Global bot configuration
│   ├── brokers/
│   │   ├── _template.json           # Broker config template
│   │   ├── binance.json             # Binance configuration
│   │   ├── coinbase.json            # Coinbase configuration
│   │   └── ...
│   └── strategies/
│       └── strategy_config.json     # Strategy configurations
```

---

## Environment Variables

Environment variables are stored in `.env` file and used for secrets and environment-specific configuration.

### Creating .env File

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env

# Secure the file
chmod 600 .env
```

### Complete .env Reference

```bash
# =================================
# BOT CONFIGURATION
# =================================

# Bot Mode: paper, live
BOT_MODE=paper

# Log Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# =================================
# API CONFIGURATION
# =================================

# API Server Settings
API_PORT=8000
API_HOST=0.0.0.0
API_KEY=your-secure-api-key-change-this
API_RELOAD=false

# CORS Settings (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Environment
ENVIRONMENT=development

# =================================
# DATABASE CONFIGURATION
# =================================

# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_bot
DB_USER=trader
DB_PASSWORD=secure_password_change_this
DB_SSLMODE=prefer

# Database URL (alternative to individual settings)
# DATABASE_URL=postgresql://trader:password@localhost:5432/trading_bot

# =================================
# REDIS CONFIGURATION
# =================================

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Redis URL (alternative)
# REDIS_URL=redis://localhost:6379/0

# =================================
# RISK MANAGEMENT
# =================================

# Global Risk Settings
MAX_POSITION_SIZE=1000
MAX_DAILY_LOSS=500
MAX_OPEN_POSITIONS=5
MAX_PORTFOLIO_EXPOSURE=0.5

# =================================
# NOTIFICATIONS
# =================================

# Enable Notifications
ENABLE_NOTIFICATIONS=false

# Email Notifications
NOTIFICATION_EMAIL=your-email@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password

# Telegram Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Slack Notifications
SLACK_WEBHOOK_URL=

# =================================
# BROKER API KEYS
# =================================

# Binance
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=true

# Binance US
BINANCE_US_API_KEY=
BINANCE_US_API_SECRET=
BINANCE_US_TESTNET=true

# Coinbase Pro
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_PASSPHRASE=
COINBASE_SANDBOX=true

# Gemini
GEMINI_API_KEY=
GEMINI_API_SECRET=
GEMINI_SANDBOX=true

# MetaTrader 4 (Windows only)
MT4_LOGIN=
MT4_PASSWORD=
MT4_SERVER=
MT4_PATH=C:\Program Files\MetaTrader 4\terminal64.exe

# =================================
# EXTERNAL SERVICES
# =================================

# Data Providers
ALPHA_VANTAGE_API_KEY=
POLYGON_API_KEY=
FINNHUB_API_KEY=

# News/Sentiment
NEWS_API_KEY=

# =================================
# ADVANCED SETTINGS
# =================================

# Timeouts (milliseconds)
REQUEST_TIMEOUT=30000
BROKER_TIMEOUT=60000

# Retries
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY=5

# Performance
MAX_WORKERS=4
ENABLE_CACHING=true
CACHE_TTL=300

# Security
ENABLE_IP_WHITELIST=false
ALLOWED_IPS=127.0.0.1,192.168.1.100

# =================================
# DO NOT COMMIT THIS FILE!
# Add .env to .gitignore
# =================================
```

### Environment Variable Types

#### Required Variables

These must be set for the bot to function:

```bash
API_KEY=your-api-key
DB_PASSWORD=your-db-password
```

#### Optional Variables

These have defaults but can be overridden:

```bash
API_PORT=8000                    # Default: 8000
LOG_LEVEL=INFO                   # Default: INFO
BOT_MODE=paper                   # Default: paper
```

#### Broker-Specific Variables

Set only for brokers you're using:

```bash
BINANCE_API_KEY=...             # Only if using Binance
COINBASE_API_KEY=...            # Only if using Coinbase
```

### Accessing Environment Variables

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
api_key = os.getenv('API_KEY')
db_host = os.getenv('DB_HOST', 'localhost')  # With default
log_level = os.getenv('LOG_LEVEL', 'INFO')
```

---

## Global Configuration

Global configuration is stored in `config/global.json` and contains bot-wide settings.

### Complete global.json

```json
{
  "bot_name": "MVP Trading Bot",
  "version": "1.0.0",
  "mode": "paper",
  
  "logging": {
    "level": "INFO",
    "format": "json",
    "output": "console",
    "log_file": "logs/trading_bot.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "log_to_file": true,
    "log_to_console": true,
    "colored_output": true
  },
  
  "execution": {
    "update_interval": 60,
    "max_concurrent_orders": 5,
    "order_timeout": 300,
    "retry_attempts": 3,
    "retry_delay": 5,
    "enable_paper_trading": true,
    "sync_interval": 300
  },
  
  "risk_management": {
    "max_position_size": 1000,
    "max_daily_loss": 500,
    "max_open_positions": 5,
    "max_portfolio_exposure": 0.5,
    "position_size_type": "fixed",
    "emergency_stop_loss": 10.0,
    "max_drawdown": 15.0,
    "correlation_limit": 0.7,
    "volatility_filter": true,
    "max_volatility": 0.05
  },
  
  "data": {
    "timeframe": "1h",
    "lookback_period": 100,
    "data_source": "exchange",
    "cache_enabled": true,
    "cache_ttl": 300,
    "warmup_period": 200,
    "data_providers": ["exchange", "fallback"]
  },
  
  "notifications": {
    "enabled": false,
    "channels": ["console"],
    "events": [
      "trade_executed",
      "stop_loss_hit",
      "take_profit_hit",
      "error",
      "bot_started",
      "bot_stopped",
      "strategy_enabled",
      "strategy_disabled"
    ],
    "email": {
      "enabled": false,
      "recipients": []
    },
    "telegram": {
      "enabled": false
    },
    "slack": {
      "enabled": false
    },
    "webhook": {
      "enabled": false,
      "url": ""
    }
  },
  
  "database": {
    "enabled": true,
    "type": "postgresql",
    "track_trades": true,
    "track_performance": true,
    "track_orders": true,
    "track_balances": true,
    "retention_days": 365,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600
  },
  
  "redis": {
    "enabled": true,
    "use_cache": true,
    "use_queue": true,
    "use_pubsub": true,
    "key_prefix": "tradingbot:",
    "default_ttl": 300
  },
  
  "api": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 8000,
    "reload": false,
    "workers": 1,
    "cors_enabled": true,
    "rate_limit_enabled": false,
    "rate_limit_requests": 100,
    "rate_limit_period": 60,
    "enable_docs": true,
    "enable_metrics": true
  },
  
  "features": {
    "enable_backtesting": true,
    "enable_paper_trading": true,
    "enable_live_trading": false,
    "enable_api": true,
    "enable_websockets": true,
    "enable_ml_features": false,
    "enable_sentiment_analysis": false,
    "enable_portfolio_optimization": false
  },
  
  "performance": {
    "enable_profiling": false,
    "enable_metrics": true,
    "metrics_interval": 60,
    "memory_limit_mb": 2048,
    "cpu_limit_percent": 80
  },
  
  "security": {
    "enable_ip_whitelist": false,
    "allowed_ips": [],
    "enable_rate_limiting": true,
    "max_login_attempts": 5,
    "session_timeout": 3600,
    "require_https": false
  }
}
```

### Configuration Sections

#### Logging Settings

```json
"logging": {
  "level": "INFO",                 // DEBUG, INFO, WARNING, ERROR, CRITICAL
  "format": "json",                // json, text, colored
  "output": "console",             // console, file, both
  "log_file": "logs/trading_bot.log",
  "max_file_size": "10MB",        // Maximum log file size
  "backup_count": 5,              // Number of backup files
  "log_to_file": true,
  "log_to_console": true,
  "colored_output": true
}
```

#### Execution Settings

```json
"execution": {
  "update_interval": 60,          // Seconds between strategy updates
  "max_concurrent_orders": 5,     // Maximum simultaneous orders
  "order_timeout": 300,           // Order timeout in seconds
  "retry_attempts": 3,            // Number of retry attempts
  "retry_delay": 5,               // Delay between retries (seconds)
  "enable_paper_trading": true,
  "sync_interval": 300            // Seconds between data syncs
}
```

#### Risk Management Settings

```json
"risk_management": {
  "max_position_size": 1000,          // Max position size in base currency
  "max_daily_loss": 500,              // Max daily loss limit
  "max_open_positions": 5,            // Max concurrent positions
  "max_portfolio_exposure": 0.5,      // Max 50% portfolio exposure
  "position_size_type": "fixed",      // fixed, percentage, risk_based
  "emergency_stop_loss": 10.0,        // Emergency stop at 10% loss
  "max_drawdown": 15.0,               // Max drawdown percentage
  "correlation_limit": 0.7,           // Max correlation between positions
  "volatility_filter": true,          // Filter by volatility
  "max_volatility": 0.05              // Maximum acceptable volatility
}
```

#### Data Settings

```json
"data": {
  "timeframe": "1h",              // Default timeframe
  "lookback_period": 100,         // Candles to fetch
  "data_source": "exchange",      // exchange, database, file
  "cache_enabled": true,
  "cache_ttl": 300,               // Cache time-to-live (seconds)
  "warmup_period": 200,           // Initial data for indicators
  "data_providers": ["exchange", "fallback"]
}
```

---

## Broker Configuration

Broker configurations are stored in `config/brokers/` directory.

### Broker Configuration Template

`config/brokers/_template.json`:

```json
{
  "name": "broker_name",
  "type": "crypto",
  "enabled": false,
  "description": "Broker description",
  
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
    "recv_window": 5000,
    "request_timeout": 30000,
    "max_retries": 3
  },
  
  "supported_pairs": [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT"
  ],
  
  "trading_settings": {
    "default_order_type": "limit",
    "default_time_in_force": "GTC",
    "enable_margin": false,
    "enable_futures": false,
    "slippage_tolerance": 0.001,
    "min_order_size": 10.0,
    "max_order_size": 10000.0
  },
  
  "risk_management": {
    "max_position_size": 1000,
    "max_leverage": 1,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 5.0,
    "trailing_stop": false,
    "trailing_stop_distance": 1.0
  },
  
  "fees": {
    "maker_fee": 0.001,
    "taker_fee": 0.001,
    "withdrawal_fee": 0.0005
  },
  
  "custom_settings": {
    "note": "Add any broker-specific settings here"
  }
}
```

### Example: Binance Configuration

`config/brokers/binance.json`:

```json
{
  "name": "binance",
  "type": "crypto",
  "enabled": true,
  "description": "Binance cryptocurrency exchange",
  
  "api_credentials": {
    "api_key": "${BINANCE_API_KEY}",
    "api_secret": "${BINANCE_API_SECRET}"
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
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "ADA/USDT",
    "DOT/USDT"
  ],
  
  "trading_settings": {
    "default_order_type": "limit",
    "default_time_in_force": "GTC",
    "enable_margin": false,
    "enable_futures": false
  },
  
  "risk_management": {
    "max_position_size": 10000,
    "max_leverage": 1,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 5.0
  }
}
```

### Broker Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique broker identifier |
| `type` | string | Yes | Broker type (crypto, forex, stocks) |
| `enabled` | boolean | Yes | Whether broker is enabled |
| `api_credentials` | object | Yes | API authentication credentials |
| `settings` | object | Yes | Broker-specific settings |
| `supported_pairs` | array | No | List of supported trading pairs |
| `trading_settings` | object | No | Trading preferences |
| `risk_management` | object | No | Broker-specific risk settings |

---

## Strategy Configuration

Strategy configurations are stored in `config/strategies/strategy_config.json`.

### Complete Strategy Configuration

```json
{
  "active_strategies": [
    "sma_crossover",
    "rsi_bb",
    "momentum"
  ],
  
  "strategies": {
    "sma_crossover": {
      "enabled": true,
      "description": "Simple Moving Average Crossover Strategy",
      "class": "SMACrossoverStrategy",
      
      "parameters": {
        "fast_period": 10,
        "slow_period": 30,
        "symbol": "BTC/USDT",
        "timeframe": "1h"
      },
      
      "risk_settings": {
        "position_size": 100,
        "position_size_type": "fixed",
        "stop_loss_pct": 2.0,
        "take_profit_pct": 5.0,
        "trailing_stop": false,
        "trailing_stop_pct": 1.0,
        "max_positions": 1
      },
      
      "scheduling": {
        "active_hours": [0, 23],
        "active_days": [0, 1, 2, 3, 4, 5, 6],
        "timezone": "UTC"
      }
    },
    
    "rsi_bb": {
      "enabled": true,
      "description": "RSI + Bollinger Bands Mean Reversion",
      "class": "RSIBBStrategy",
      
      "parameters": {
        "rsi_period": 14,
        "rsi_overbought": 70,
        "rsi_oversold": 30,
        "bb_period": 20,
        "bb_std": 2,
        "symbol": "ETH/USDT",
        "timeframe": "1h"
      },
      
      "risk_settings": {
        "position_size": 100,
        "stop_loss_pct": 2.0,
        "take_profit_pct": 5.0
      }
    },
    
    "macd": {
      "enabled": false,
      "description": "MACD Momentum Strategy",
      "class": "MACDStrategy",
      
      "parameters": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9,
        "symbol": "BTC/USDT",
        "timeframe": "4h"
      },
      
      "risk_settings": {
        "position_size": 200,
        "stop_loss_pct": 3.0,
        "take_profit_pct": 7.0
      }
    },
    
    "momentum": {
      "enabled": true,
      "description": "Volume-Weighted Momentum Strategy",
      "class": "MomentumStrategy",
      
      "parameters": {
        "momentum_period": 20,
        "volume_period": 20,
        "momentum_threshold": 0.03,
        "volume_multiplier": 1.5,
        "symbol": "BTC/USDT",
        "timeframe": "1h"
      },
      
      "risk_settings": {
        "position_size": 150,
        "stop_loss_pct": 3.0,
        "take_profit_pct": 8.0
      }
    }
  },
  
  "backtest_settings": {
    "initial_capital": 10000,
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "commission": 0.001,
    "slippage": 0.0005,
    "enable_compounding": true
  },
  
  "optimization": {
    "enabled": false,
    "method": "grid_search",
    "metric": "sharpe_ratio",
    "cross_validation": true,
    "train_test_split": 0.7
  }
}
```

### Strategy Configuration Fields

#### Main Fields

| Field | Type | Description |
|-------|------|-------------|
| `active_strategies` | array | List of enabled strategy IDs |
| `strategies` | object | Strategy definitions |
| `backtest_settings` | object | Backtesting configuration |
| `optimization` | object | Strategy optimization settings |

#### Per-Strategy Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | Yes | Whether strategy is active |
| `description` | string | No | Strategy description |
| `class` | string | Yes | Strategy class name |
| `parameters` | object | Yes | Strategy-specific parameters |
| `risk_settings` | object | Yes | Risk management settings |
| `scheduling` | object | No | Time-based scheduling |

#### Risk Settings

```json
"risk_settings": {
  "position_size": 100,           // Position size
  "position_size_type": "fixed",  // fixed, percentage, risk_based
  "stop_loss_pct": 2.0,          // Stop loss percentage
  "take_profit_pct": 5.0,        // Take profit percentage
  "trailing_stop": false,         // Enable trailing stop
  "trailing_stop_pct": 1.0,      // Trailing stop percentage
  "max_positions": 1,             // Max concurrent positions
  "risk_per_trade": 1.0,         // Risk percentage per trade
  "position_correlation": 0.7     // Max correlation with other positions
}
```

---

## Risk Management Settings

Risk management can be configured at multiple levels:

### Global Risk Management

In `config/global.json`:

```json
"risk_management": {
  "max_position_size": 1000,
  "max_daily_loss": 500,
  "max_open_positions": 5,
  "max_portfolio_exposure": 0.5,
  "position_size_type": "fixed",
  "emergency_stop_loss": 10.0,
  "max_drawdown": 15.0,
  "correlation_limit": 0.7,
  "volatility_filter": true,
  "max_volatility": 0.05
}
```

### Broker-Level Risk Management

In `config/brokers/broker_name.json`:

```json
"risk_management": {
  "max_position_size": 10000,
  "max_leverage": 1,
  "stop_loss_percentage": 2.0,
  "take_profit_percentage": 5.0
}
```

### Strategy-Level Risk Management

In `config/strategies/strategy_config.json`:

```json
"risk_settings": {
  "position_size": 100,
  "stop_loss_pct": 2.0,
  "take_profit_pct": 5.0,
  "trailing_stop": true,
  "trailing_stop_pct": 1.0
}
```

### Risk Management Priority

```
Strategy Settings > Broker Settings > Global Settings
```

### Position Sizing Methods

#### Fixed Size

```json
{
  "position_size": 1000,
  "position_size_type": "fixed"
}
```

#### Percentage of Portfolio

```json
{
  "position_size_pct": 10,
  "position_size_type": "percentage"
}
```

#### Risk-Based (Kelly Criterion)

```json
{
  "risk_per_trade": 1.0,
  "position_size_type": "risk_based"
}
```

---

## Logging Configuration

### Log Levels

- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

### Log Formats

#### JSON Format

```json
{
  "timestamp": "2024-01-15T12:30:00.000Z",
  "level": "INFO",
  "logger": "bot.main",
  "message": "Trading bot started",
  "context": {...}
}
```

#### Text Format

```
2024-01-15 12:30:00 - bot.main - INFO - Trading bot started
```

#### Colored Format

Colored console output for better readability.

### Log Configuration

```json
"logging": {
  "level": "INFO",
  "format": "json",
  "output": "both",
  "log_file": "logs/trading_bot.log",
  "max_file_size": "10MB",
  "backup_count": 5,
  "log_to_file": true,
  "log_to_console": true,
  "colored_output": true
}
```

### Log Rotation

Logs are automatically rotated when they reach `max_file_size`.

```
logs/trading_bot.log          # Current log
logs/trading_bot.log.1        # Previous log
logs/trading_bot.log.2        # Older log
...
logs/trading_bot.log.5        # Oldest log (deleted on next rotation)
```

---

## Database Configuration

### PostgreSQL Configuration

```json
"database": {
  "enabled": true,
  "type": "postgresql",
  "track_trades": true,
  "track_performance": true,
  "track_orders": true,
  "track_balances": true,
  "retention_days": 365,
  "pool_size": 5,
  "max_overflow": 10,
  "pool_timeout": 30,
  "pool_recycle": 3600
}
```

### Environment Variables

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_bot
DB_USER=trader
DB_PASSWORD=secure_password
DB_SSLMODE=prefer

# Or use connection URL
DATABASE_URL=postgresql://trader:password@localhost:5432/trading_bot
```

### Connection Pool Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `pool_size` | Number of connections to maintain | 5 |
| `max_overflow` | Max additional connections | 10 |
| `pool_timeout` | Timeout for getting connection | 30 |
| `pool_recycle` | Recycle connections after (seconds) | 3600 |

---

## Redis Configuration

### Redis Settings

```json
"redis": {
  "enabled": true,
  "use_cache": true,
  "use_queue": true,
  "use_pubsub": true,
  "key_prefix": "tradingbot:",
  "default_ttl": 300
}
```

### Environment Variables

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Or use connection URL
REDIS_URL=redis://localhost:6379/0
```

### Redis Use Cases

- **Caching:** Market data and calculations
- **Queue:** Async task processing
- **Pub/Sub:** Real-time notifications
- **Session:** API session management

---

## Docker Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  trading-bot:
    build: .
    container_name: trading-bot
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
  
  postgres:
    image: postgres:15-alpine
    container_name: trading-bot-db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    container_name: trading-bot-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Docker Environment

```bash
# .env for Docker
DB_HOST=postgres
REDIS_HOST=redis
API_HOST=0.0.0.0
```

---

## Configuration Validation

### Validation Script

```python
#!/usr/bin/env python3
"""
Configuration validation script
"""

import os
import json
from pathlib import Path

def validate_config():
    """Validate all configuration files"""
    errors = []
    
    # Check .env file
    if not Path('.env').exists():
        errors.append("❌ .env file not found")
    else:
        print("✅ .env file found")
    
    # Check global config
    global_config_path = Path('config/global.json')
    if not global_config_path.exists():
        errors.append("❌ config/global.json not found")
    else:
        try:
            with open(global_config_path) as f:
                config = json.load(f)
            print("✅ global.json is valid JSON")
            
            # Validate required fields
            required = ['bot_name', 'version', 'mode']
            for field in required:
                if field not in config:
                    errors.append(f"❌ Missing required field in global.json: {field}")
        except json.JSONDecodeError as e:
            errors.append(f"❌ Invalid JSON in global.json: {e}")
    
    # Check broker configs
    broker_dir = Path('config/brokers')
    if not broker_dir.exists():
        errors.append("❌ config/brokers/ directory not found")
    else:
        broker_configs = list(broker_dir.glob('*.json'))
        if not broker_configs:
            errors.append("⚠️  No broker configurations found")
        else:
            for broker_file in broker_configs:
                if broker_file.name == '_template.json':
                    continue
                try:
                    with open(broker_file) as f:
                        broker = json.load(f)
                    print(f"✅ {broker_file.name} is valid")
                except json.JSONDecodeError as e:
                    errors.append(f"❌ Invalid JSON in {broker_file.name}: {e}")
    
    # Print summary
    print("\n" + "="*60)
    if errors:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ All configurations are valid!")
        return True

if __name__ == '__main__':
    validate_config()
```

### Running Validation

```bash
python scripts/validate_config.py
```

---

## Common Scenarios

### Scenario 1: Development Setup

```bash
# .env
BOT_MODE=paper
LOG_LEVEL=DEBUG
BINANCE_TESTNET=true
COINBASE_SANDBOX=true
API_RELOAD=true
ENVIRONMENT=development
```

```json
// config/global.json
{
  "mode": "paper",
  "logging": {
    "level": "DEBUG",
    "output": "console"
  },
  "execution": {
    "update_interval": 60
  }
}
```

### Scenario 2: Production Setup

```bash
# .env
BOT_MODE=live
LOG_LEVEL=INFO
BINANCE_TESTNET=false
API_RELOAD=false
ENVIRONMENT=production
```

```json
// config/global.json
{
  "mode": "live",
  "logging": {
    "level": "INFO",
    "output": "both",
    "log_to_file": true
  },
  "execution": {
    "update_interval": 30
  },
  "security": {
    "require_https": true,
    "enable_ip_whitelist": true
  }
}
```

### Scenario 3: Backtesting

```json
{
  "mode": "backtest",
  "features": {
    "enable_backtesting": true,
    "enable_paper_trading": false,
    "enable_live_trading": false,
    "enable_api": false
  },
  "backtest_settings": {
    "initial_capital": 10000,
    "start_date": "2023-01-01",
    "end_date": "2024-01-01"
  }
}
```

### Scenario 4: Multiple Strategies

```json
{
  "active_strategies": [
    "sma_crossover_btc",
    "rsi_bb_eth",
    "macd_sol"
  ],
  "strategies": {
    "sma_crossover_btc": {
      "enabled": true,
      "parameters": {"symbol": "BTC/USDT"}
    },
    "rsi_bb_eth": {
      "enabled": true,
      "parameters": {"symbol": "ETH/USDT"}
    },
    "macd_sol": {
      "enabled": true,
      "parameters": {"symbol": "SOL/USDT"}
    }
  }
}
```

### Scenario 5: High-Frequency Trading

```json
{
  "execution": {
    "update_interval": 5,
    "max_concurrent_orders": 20,
    "order_timeout": 30
  },
  "data": {
    "timeframe": "1m",
    "cache_enabled": true,
    "cache_ttl": 10
  },
  "performance": {
    "max_workers": 8,
    "enable_caching": true
  }
}
```

---

## Conclusion

This configuration reference covers all available settings. Key takeaways:

1. **Use environment variables** for secrets
2. **Validate configurations** before running
3. **Start with defaults** and adjust as needed
4. **Test in paper mode** before going live
5. **Monitor and adjust** based on performance

For additional help:
- [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) - Strategy development
- [BROKER_SETUP.md](BROKER_SETUP.md) - Broker configuration
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation

Happy trading! 🚀
