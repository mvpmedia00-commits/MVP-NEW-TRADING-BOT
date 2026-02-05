# 🚀 MVP Trading Bot

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

**A professional, multi-broker cryptocurrency and forex trading automation system**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Supported Brokers](#-supported-brokers)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [Development](#-development)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🎯 Overview

The **MVP Trading Bot** is a sophisticated, production-ready automated trading system designed for both cryptocurrency and forex markets. Built with modularity and extensibility in mind, it provides a robust framework for developing, testing, and deploying algorithmic trading strategies across multiple broker platforms.

### Key Highlights

- **🔄 Multi-Broker Support**: Trade across Binance, Coinbase Pro, Gemini, and MetaTrader 4
- **📊 Pre-Built Strategies**: SMA Crossover, EMA, MACD, RSI+Bollinger Bands
- **🔒 Risk Management**: Built-in position sizing, stop-loss, take-profit, and daily loss limits
- **🧪 Paper Trading**: Test strategies risk-free before going live
- **📈 Backtesting**: Validate strategies on historical data
- **🌐 REST API**: Full-featured API for monitoring and control
- **🐳 Docker Ready**: Complete containerized deployment
- **📊 Portfolio Tracking**: Real-time monitoring and performance analytics

---

## ✨ Features

### Core Trading Features

- **Automated Strategy Execution**: Run multiple strategies simultaneously
- **Real-Time Market Data**: Live price feeds and OHLCV data from exchanges
- **Order Management**: Market and limit orders with retry logic
- **Position Tracking**: Monitor open positions, P&L, and portfolio value
- **Multi-Timeframe Support**: Trade on any timeframe (1m, 5m, 1h, 1d, etc.)

### Risk Management

- **Position Sizing**: Fixed or percentage-based position sizing
- **Stop-Loss Orders**: Automatic stop-loss execution
- **Take-Profit Targets**: Configurable profit-taking levels
- **Daily Loss Limits**: Prevent excessive losses in volatile markets
- **Maximum Open Positions**: Control risk exposure
- **Emergency Stop**: Immediate position closure and bot shutdown

### Strategy Development

- **Extensible Framework**: Easy-to-use base classes for custom strategies
- **Technical Indicators**: 100+ indicators via TA-Lib integration
- **Backtesting Engine**: Test strategies on historical data
- **Paper Trading Mode**: Simulate trades without real capital
- **Strategy Templates**: Ready-to-use templates for custom development

### Monitoring & Control

- **REST API**: Full API for programmatic control
- **Real-Time Portfolio**: Live portfolio status and positions
- **Trade History**: Detailed trade logs and analytics
- **Performance Metrics**: Win rate, Sharpe ratio, max drawdown
- **Health Monitoring**: System health checks and diagnostics

### Infrastructure

- **PostgreSQL Database**: Persistent storage for trades and performance
- **Redis Cache**: Fast data access and caching
- **Docker Support**: Production-ready containerization
- **Logging**: Comprehensive JSON-formatted logging
- **Environment Configuration**: Flexible .env-based configuration

---

## 🏦 Supported Brokers

### Cryptocurrency Exchanges

| Broker | Status | Test Mode | Markets | Features |
|--------|--------|-----------|---------|----------|
| **Binance** | ✅ Production | ✅ Testnet | Spot | Full OHLCV, Order book |
| **Binance US** | ✅ Production | ✅ Testnet | Spot | Full OHLCV, Order book |
| **Coinbase Pro** | ✅ Production | ✅ Sandbox | Spot | Full OHLCV, Order book |
| **Gemini** | ✅ Production | ✅ Sandbox | Spot | Full OHLCV, Order book |

### Forex Brokers

| Broker | Status | Test Mode | Markets | Platform |
|--------|--------|-----------|---------|----------|
| **MetaTrader 4** | ✅ Production | ✅ Demo | Forex, CFD | MT4 API |

All brokers support:
- ✅ Real-time price data
- ✅ Historical OHLCV data
- ✅ Market and limit orders
- ✅ Balance and position queries
- ✅ Order status tracking

See [BROKER_SETUP.md](BROKER_SETUP.md) for detailed configuration instructions.

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **PostgreSQL**: 15.x (or Docker)
- **Redis**: 7.x (or Docker)
- **TA-Lib**: For technical indicators
- **Docker**: (Optional) For containerized deployment

### Installation

#### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT

# Install TA-Lib (OS-specific)
# Ubuntu/Debian:
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..

# macOS:
brew install ta-lib

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Setup PostgreSQL and Redis (local or Docker)
docker run -d --name postgres -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 postgres:15-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings
```

#### Option 2: Docker Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f trading_bot
```

See [INSTALLATION.md](INSTALLATION.md) for detailed installation instructions for all platforms.

### Initial Configuration

1. **Set up environment variables** (`.env`):
```bash
BOT_MODE=paper              # Start in paper trading mode
LOG_LEVEL=INFO              # Logging level
API_KEY=your-secure-key     # API key for REST API
```

2. **Configure a broker** (`config/brokers/binance.json`):
```json
{
  "name": "binance",
  "type": "crypto",
  "enabled": true,
  "api_key": "${BINANCE_API_KEY}",
  "api_secret": "${BINANCE_API_SECRET}",
  "testnet": true
}
```

3. **Configure a strategy** (`config/strategies/strategies.json`):
```json
{
  "active_strategies": ["sma_crossover"],
  "strategies": {
    "sma_crossover": {
      "enabled": true,
      "parameters": {
        "symbol": "BTC/USDT",
        "fast_period": 10,
        "slow_period": 30
      }
    }
  }
}
```

### Running the Bot

#### Paper Trading (Recommended for First Run)

```bash
# Local
./scripts/start_bot.sh

# Docker
docker-compose up -d trading_bot
docker-compose logs -f trading_bot
```

#### Live Trading

```bash
# Set BOT_MODE=live in .env file
nano .env

# Start bot
./scripts/start_bot.sh --mode live

# Or with Docker
docker-compose up -d trading_bot
```

### Accessing the API

The REST API runs on port 8000 by default:

```bash
# Check bot health
curl -H "X-API-Key: your-api-key" http://localhost:8000/health

# Get portfolio status
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/portfolio/status

# View API documentation
open http://localhost:8000/docs
```

---

## 🏗 Architecture

The MVP Trading Bot follows a modular, service-oriented architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        Trading Bot                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Brokers    │  │  Strategies  │  │     API      │    │
│  │              │  │              │  │              │    │
│  │  - Binance   │  │  - SMA       │  │  - Portfolio │    │
│  │  - Coinbase  │  │  - EMA       │  │  - Trades    │    │
│  │  - Gemini    │  │  - MACD      │  │  - Control   │    │
│  │  - MT4       │  │  - RSI+BB    │  │  - Strategies│    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │             │
│         └─────────────────┴─────────────────┘             │
│                          │                                │
│              ┌───────────▼───────────┐                    │
│              │    Core Services      │                    │
│              │                       │                    │
│              │  - Portfolio Manager  │                    │
│              │  - Order Manager      │                    │
│              │  - Risk Manager       │                    │
│              │  - Data Manager       │                    │
│              └───────────┬───────────┘                    │
│                          │                                │
└──────────────────────────┼────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐      ┌────▼─────┐      ┌────▼─────┐
   │PostgreSQL│      │  Redis   │      │   Logs   │
   │ Database │      │  Cache   │      │  JSON    │
   └──────────┘      └──────────┘      └──────────┘
```

### Component Overview

#### 1. **Brokers Layer**
- Abstract `BaseBroker` interface
- Exchange-specific implementations (Binance, Coinbase, Gemini, MT4)
- Unified API for market data and order execution
- Connection management and error handling

#### 2. **Strategies Layer**
- Abstract `BaseStrategy` base class
- Pre-built strategies (SMA, EMA, MACD, RSI+BB)
- Custom strategy support
- Signal generation and position management

#### 3. **Core Services**
- **Portfolio Manager**: Track positions, balances, and P&L
- **Order Manager**: Execute and manage orders
- **Risk Manager**: Enforce risk limits and position sizing
- **Data Manager**: Fetch and cache market data

#### 4. **API Layer**
- RESTful API built with FastAPI
- Authentication via API keys
- Real-time portfolio and trade monitoring
- Bot control endpoints (start, stop, emergency stop)

#### 5. **Data Storage**
- **PostgreSQL**: Persistent storage for trades and performance
- **Redis**: Fast caching for market data and state
- **JSON Logs**: Structured logging for debugging

### Data Flow

1. **Market Data Collection**: Brokers fetch real-time price and OHLCV data
2. **Indicator Calculation**: Strategies calculate technical indicators
3. **Signal Generation**: Strategies generate BUY/SELL/HOLD signals
4. **Risk Assessment**: Risk Manager validates position size and limits
5. **Order Execution**: Order Manager executes trades via broker
6. **Position Tracking**: Portfolio Manager updates positions and P&L
7. **Persistence**: Trades and performance saved to database

---

## 📚 Documentation

Comprehensive documentation is available:

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Detailed installation guide for all platforms |
| [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) | Complete guide to creating and using strategies |
| [BROKER_SETUP.md](BROKER_SETUP.md) | Broker configuration for all supported exchanges |
| [ADDING_BROKERS.md](ADDING_BROKERS.md) | Guide to adding new broker integrations |
| [API_REFERENCE.md](API_REFERENCE.md) | Complete REST API documentation |
| [CONFIGURATION.md](CONFIGURATION.md) | All configuration options explained |

---

## 🛠 Technology Stack

### Core Technologies

- **Python 3.11**: Modern Python with type hints and async support
- **FastAPI**: High-performance async web framework
- **SQLAlchemy 2.0**: Modern ORM with async support
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### Trading & Market Data

- **CCXT**: Cryptocurrency exchange API wrapper
- **TA-Lib**: Technical analysis indicators
- **MetaTrader5**: Forex trading platform integration

### Infrastructure

- **PostgreSQL 15**: Relational database
- **Redis 7**: In-memory cache
- **Docker**: Containerization
- **Uvicorn**: ASGI web server

### Development Tools

- **Pydantic**: Data validation and settings management
- **python-dotenv**: Environment variable management
- **pytest**: Testing framework

---

## 📁 Project Structure

```
MVP-NEW-TRADING-BOT/
│
├── 📁 bot/                          # Core trading engine
│   ├── main.py                     # Main bot orchestrator
│   ├── 📁 brokers/                 # Broker implementations
│   │   ├── base_broker.py          # Abstract broker interface
│   │   ├── binance_broker.py       # Binance integration
│   │   ├── coinbase_broker.py      # Coinbase Pro integration
│   │   ├── gemini_broker.py        # Gemini integration
│   │   └── mt4_broker.py           # MetaTrader 4 integration
│   │
│   ├── 📁 strategies/              # Trading strategies
│   │   ├── base_strategy.py        # Abstract strategy base
│   │   ├── sma_crossover.py        # SMA crossover strategy
│   │   ├── ema_strategy.py         # EMA strategy
│   │   ├── macd_strategy.py        # MACD strategy
│   │   └── rsi_bb.py               # RSI + Bollinger Bands
│   │
│   ├── 📁 core/                    # Core services
│   │   ├── portfolio.py            # Portfolio management
│   │   ├── order_manager.py        # Order execution
│   │   ├── risk_manager.py         # Risk management
│   │   └── data_manager.py         # Market data handling
│   │
│   └── 📁 utils/                   # Utilities
│       ├── logger.py               # Logging configuration
│       └── config_loader.py        # Configuration management
│
├── 📁 api/                          # REST API
│   ├── server.py                   # FastAPI application
│   ├── 📁 routes/                  # API endpoints
│   │   ├── portfolio.py            # Portfolio routes
│   │   ├── trades.py               # Trade routes
│   │   ├── strategies.py           # Strategy routes
│   │   └── control.py              # Control routes
│   │
│   └── 📁 models/                  # Pydantic models
│       ├── portfolio.py            # Portfolio schemas
│       └── trades.py               # Trade schemas
│
├── 📁 config/                       # Configuration files
│   ├── global.json                 # Global bot configuration
│   ├── 📁 brokers/                 # Broker configs
│   │   ├── binance.json
│   │   ├── coinbase.json
│   │   ├── gemini.json
│   │   └── mt4.json
│   │
│   └── 📁 strategies/              # Strategy configs
│       └── strategies.json         # Strategy definitions
│
├── 📁 user_strategies/              # Custom user strategies
│   ├── custom_strategy_template.py # Strategy template
│   └── 📁 examples/                # Example strategies
│
├── 📁 scripts/                      # Utility scripts
│   ├── start_bot.sh                # Bot startup script
│   ├── backtest.py                 # Backtesting script
│   └── add_broker.py               # Broker setup helper
│
├── 📁 tests/                        # Test suite
│   ├── test_brokers.py
│   ├── test_strategies.py
│   └── test_api.py
│
├── 📁 data/                         # Data storage
│   ├── 📁 historical/              # Historical market data
│   └── 📁 backtest_results/        # Backtesting results
│
├── 📁 logs/                         # Application logs
│
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker services orchestration
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── .gitignore                      # Git ignore rules
```

---

## ⚙️ Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Bot Operation
BOT_MODE=paper                      # paper or live
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR

# API
API_PORT=8000
API_HOST=0.0.0.0
API_KEY=your-secure-api-key

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_bot
DB_USER=trader
DB_PASSWORD=your-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Risk Management
MAX_POSITION_SIZE=1000
MAX_DAILY_LOSS=500
MAX_OPEN_POSITIONS=5

# Broker API Keys
BINANCE_API_KEY=your-key
BINANCE_API_SECRET=your-secret
BINANCE_TESTNET=true
```

### Global Configuration

Main configuration in `config/global.json`:

```json
{
  "bot_name": "MVP Trading Bot",
  "version": "1.0.0",
  "mode": "paper",
  "execution": {
    "update_interval": 60,
    "max_concurrent_orders": 5
  },
  "risk_management": {
    "max_position_size": 1000,
    "max_daily_loss": 500
  }
}
```

See [CONFIGURATION.md](CONFIGURATION.md) for complete configuration reference.

---

## 💡 Usage Examples

### Running a Simple SMA Strategy

```bash
# 1. Configure strategy
cat > config/strategies/strategies.json <<EOF
{
  "active_strategies": ["sma_crossover"],
  "strategies": {
    "sma_crossover": {
      "enabled": true,
      "parameters": {
        "symbol": "BTC/USDT",
        "fast_period": 10,
        "slow_period": 30,
        "position_size": 100
      },
      "risk_settings": {
        "stop_loss_pct": 2.0,
        "take_profit_pct": 5.0
      }
    }
  }
}
EOF

# 2. Start bot in paper mode
./scripts/start_bot.sh

# 3. Monitor via API
curl -H "X-API-Key: your-key" http://localhost:8000/api/v1/portfolio/status
```

### Creating a Custom Strategy

```python
from bot.strategies.base_strategy import BaseStrategy
import pandas as pd

class MyStrategy(BaseStrategy):
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        # Add your indicators
        data['sma_20'] = data['close'].rolling(20).mean()
        return data
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        if data['close'].iloc[-1] > data['sma_20'].iloc[-1]:
            return 'BUY'
        return 'HOLD'
```

See [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) for complete strategy development guide.

### Backtesting a Strategy

```bash
python scripts/backtest.py \
  --strategy sma_crossover \
  --symbol BTC/USDT \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --initial-capital 10000
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bot --cov=api

# Run specific test file
pytest tests/test_strategies.py

# Run with verbose output
pytest -v
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. TA-Lib Installation Fails

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install ta-lib

# macOS
brew install ta-lib

# Windows: Download pre-built wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
```

#### 2. Database Connection Errors

**Solution**:
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres
```

#### 3. Broker API Authentication Errors

**Solution**:
1. Verify API keys in `.env` file
2. Check API key permissions on exchange
3. Ensure testnet/sandbox mode matches API keys

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚠️ Disclaimer

**IMPORTANT**: This software is for educational and research purposes only.

- Trading cryptocurrencies and forex involves significant risk
- You can lose all your invested capital
- Past performance does not guarantee future results
- Always test strategies in paper trading mode first
- Never invest more than you can afford to lose
- We are not responsible for any financial losses
- Use at your own risk

**Always perform due diligence and consult with financial advisors before trading.**

---

<div align="center">

**[⬆ Back to Top](#-mvp-trading-bot)**

Made with ❤️ by the MVP Trading Bot Team

</div>
