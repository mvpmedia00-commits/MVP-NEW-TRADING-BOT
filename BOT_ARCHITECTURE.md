# MIT Bot Architecture, User Flow, and Design

## 1. System Architecture

### Overview
MIT Bot is a modular crypto trading bot designed for live trading, backtesting, and monitoring via a FastAPI dashboard. It integrates with brokers (e.g., Gemini) using ccxt, supports multiple strategies, and is configurable via JSON files.

### Components
- **Trading Engine**: Core bot logic, manages strategies, executes trades, handles risk.
- **Strategy Manager**: Loads and runs strategies from config, supports SMA, EMA, MACD, LGM, VG, etc.
- **Broker Adapter**: Uses ccxt to connect to exchanges (Gemini, Crypto.com), handles authentication, order placement, and data fetching.
- **Config Loader**: Reads and validates JSON configs for strategies, brokers, and backtesting.
- **Backtest Module**: Simulates trading with historical data, outputs performance metrics.
- **API Server**: FastAPI app for dashboard, monitoring, and user interaction.
- **Dashboard UI**: Web interface for status, logs, performance, and manual controls.

## 2. User Flow

### 1. Setup
- User installs dependencies and activates Python environment.
- User configures broker (API keys, testnet, enabled) in `config/brokers/gemini.json`.
- User updates strategy config in `config/strategies/strategy_config.json` (pairs, parameters).

### 2. Start Bot
- User runs `python -m bot.main` to start trading engine.
- Bot loads configs, connects to broker, initializes strategies.
- Bot begins live trading or backtesting as configured.

### 3. Monitor & Control
- User runs `python -m bot.api.server` to start FastAPI dashboard.
- User accesses dashboard via browser to monitor trades, performance, logs.
- User can pause/resume bot, adjust settings, or trigger manual trades.

### 4. Error Handling
- Bot logs errors (e.g., invalid config, unsupported pairs, API failures).
- Dashboard displays error status and troubleshooting info.
- User updates configs or keys as needed and restarts bot.

## 3. Design Principles
- **Modularity**: Strategies, brokers, and configs are decoupled for easy extension.
- **Robustness**: Validates configs, handles API errors, logs all actions.
- **Transparency**: Dashboard provides real-time status, logs, and controls.
- **Security**: API keys stored in config, never hardcoded; supports testnet mode.
- **Extensibility**: New strategies and brokers can be added with minimal changes.

## 4. Mermaid Diagram

```
flowchart TD
    A[User] -->|Configures| B(Config Loader)
    B --> C{Config Files}
    C --> D[Strategy Manager]
    D --> E[Trading Engine]
    E --> F[Broker Adapter]
    F --> G[Exchange API]
    E --> H[Backtest Module]
    E --> I[Risk Manager]
    E --> J[Logger]
    E --> K[FastAPI Server]
    K --> L[Dashboard UI]
    A -->|Monitors| L
    A -->|Controls| K
```

## 5. Example User Journey
1. User sets up broker and strategy configs.
2. User starts bot and dashboard.
3. Bot connects to Gemini, loads strategies, begins trading.
4. User monitors trades and performance via dashboard.
5. If errors occur, user updates configs and restarts bot.

---

*For further customization, add new strategies in the config, or extend broker adapters for additional exchanges.*
