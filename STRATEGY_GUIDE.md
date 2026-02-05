# Trading Bot Strategy Development Guide

A comprehensive guide to developing, testing, and deploying trading strategies for the MVP Trading Bot.

## Table of Contents

1. [Introduction](#introduction)
2. [Strategy Basics](#strategy-basics)
3. [BaseStrategy Class](#basestrategy-class)
4. [Built-in Strategies](#built-in-strategies)
5. [Creating Custom Strategies](#creating-custom-strategies)
6. [Technical Indicators Reference](#technical-indicators-reference)
7. [Strategy Configuration](#strategy-configuration)
8. [Backtesting Guide](#backtesting-guide)
9. [Risk Management](#risk-management)
10. [Best Practices](#best-practices)
11. [Advanced Topics](#advanced-topics)
12. [Complete Examples](#complete-examples)
13. [Troubleshooting](#troubleshooting)

---

## Introduction

The MVP Trading Bot provides a flexible framework for implementing automated trading strategies. This guide covers everything from basic concepts to advanced strategy development.

### What You'll Learn

- How to create custom trading strategies
- Understanding the BaseStrategy class
- Working with technical indicators
- Backtesting and optimization
- Risk management implementation
- Best practices for production deployment

---

## Strategy Basics

### What is a Trading Strategy?

A trading strategy is a set of rules that determine when to enter and exit trades. In this bot, strategies:

- Analyze market data (OHLCV)
- Calculate technical indicators
- Generate trading signals (BUY, SELL, HOLD)
- Manage position entry and exit
- Implement risk management rules

### Strategy Lifecycle

```
1. Initialize → Load configuration and parameters
2. Connect → Receive market data updates
3. Calculate → Compute technical indicators
4. Analyze → Generate trading signals
5. Execute → Enter/exit positions based on signals
6. Monitor → Track performance and risk
```

---

## BaseStrategy Class

All strategies must inherit from `BaseStrategy` and implement required abstract methods.

### Class Overview

```python
from bot.strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Dict, Any

class MyStrategy(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Your initialization code
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate and add indicators to dataframe
        pass
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        # Return 'BUY', 'SELL', or 'HOLD'
        pass
```

### Required Methods

#### `__init__(self, config: Dict[str, Any])`

Initialize your strategy with configuration parameters.

**Available Config Properties:**
- `self.config` - Full configuration dictionary
- `self.name` - Strategy class name
- `self.parameters` - Strategy-specific parameters
- `self.risk_settings` - Risk management settings
- `self.enabled` - Whether strategy is active

**Example:**
```python
def __init__(self, config: Dict[str, Any]):
    super().__init__(config)
    self.period = self.parameters.get('period', 20)
    self.threshold = self.parameters.get('threshold', 0.02)
```

#### `calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame`

Calculate technical indicators needed for your strategy.

**Input:** DataFrame with OHLCV columns: `open`, `high`, `low`, `close`, `volume`

**Output:** DataFrame with added indicator columns

**Example:**
```python
def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df['sma'] = df['close'].rolling(window=self.period).mean()
    df['std'] = df['close'].rolling(window=self.period).std()
    return df
```

#### `generate_signal(self, data: pd.DataFrame) -> str`

Generate trading signal based on current market conditions.

**Returns:** One of:
- `'BUY'` - Enter long position
- `'SELL'` - Enter short position or exit long
- `'HOLD'` - No action

**Example:**
```python
def generate_signal(self, data: pd.DataFrame) -> str:
    df = self.calculate_indicators(data)
    
    if len(df) < self.period:
        return 'HOLD'
    
    current_price = df['close'].iloc[-1]
    sma = df['sma'].iloc[-1]
    
    if current_price > sma:
        return 'BUY'
    elif current_price < sma:
        return 'SELL'
    
    return 'HOLD'
```

### Optional Methods

These methods have default implementations but can be overridden:

#### `should_enter(self, data: pd.DataFrame) -> bool`

Determine if should enter a new position.

#### `should_exit(self, data: pd.DataFrame, current_price: float) -> bool`

Determine if should exit current position.

#### `get_position_size(self) -> float`

Calculate position size based on risk settings.

### Position Management

Built-in position tracking:

```python
# Track current position
self.position  # None, 'LONG', or 'SHORT'
self.entry_price  # Entry price for current position

# Enter position
self.enter_position('LONG', 50000.0)

# Exit position
self.exit_position()
```

### Risk Management

Built-in stop loss and take profit:

```python
# Automatic checks
self.check_stop_loss(current_price)  # Returns bool
self.check_take_profit(current_price)  # Returns bool

# Configuration (in risk_settings)
{
    "stop_loss_pct": 2.0,      # 2% stop loss
    "take_profit_pct": 5.0,    # 5% take profit
    "position_size": 1000      # Position size in base currency
}
```

---

## Built-in Strategies

### 1. SMA Crossover Strategy

Simple Moving Average crossover strategy.

**File:** `bot/strategies/sma_crossover.py`

**Signal Logic:**
- BUY: Fast SMA crosses above slow SMA
- SELL: Fast SMA crosses below slow SMA

**Parameters:**
```json
{
    "fast_period": 10,
    "slow_period": 30,
    "symbol": "BTC/USDT"
}
```

**Example Usage:**
```python
from bot.strategies.sma_crossover import SMACrossoverStrategy

config = {
    "parameters": {
        "fast_period": 10,
        "slow_period": 30
    },
    "risk_settings": {
        "stop_loss_pct": 2.0,
        "take_profit_pct": 5.0
    }
}

strategy = SMACrossoverStrategy(config)
signal = strategy.generate_signal(market_data)
```

**Best For:**
- Trending markets
- Medium to long-term trading
- Clear directional movements

### 2. EMA Strategy

Exponential Moving Average trend following strategy.

**File:** `bot/strategies/ema_strategy.py`

**Signal Logic:**
- BUY: Short EMA > Medium EMA > Long EMA
- SELL: Short EMA < Medium EMA < Long EMA

**Parameters:**
```json
{
    "short_period": 9,
    "medium_period": 21,
    "long_period": 50,
    "symbol": "ETH/USDT"
}
```

**Best For:**
- Trending markets
- Fast market reactions
- Crypto and forex

### 3. MACD Strategy

Moving Average Convergence Divergence strategy.

**File:** `bot/strategies/macd_strategy.py`

**Signal Logic:**
- BUY: MACD line crosses above signal line
- SELL: MACD line crosses below signal line

**Parameters:**
```json
{
    "fast_period": 12,
    "slow_period": 26,
    "signal_period": 9,
    "symbol": "BTC/USDT"
}
```

**Best For:**
- Momentum trading
- Identifying trend changes
- All market types

### 4. RSI + Bollinger Bands Strategy

Combined RSI and Bollinger Bands mean reversion strategy.

**File:** `bot/strategies/rsi_bb.py`

**Signal Logic:**
- BUY: RSI < 30 (oversold) AND price < lower Bollinger Band
- SELL: RSI > 70 (overbought) AND price > upper Bollinger Band

**Parameters:**
```json
{
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "bb_period": 20,
    "bb_std": 2,
    "symbol": "ETH/USDT"
}
```

**Best For:**
- Range-bound markets
- Mean reversion trading
- High volatility conditions

---

## Creating Custom Strategies

### Step 1: Create Strategy File

Create a new file in `user_strategies/` directory:

```bash
touch user_strategies/my_custom_strategy.py
```

### Step 2: Implement Strategy Class

```python
"""
My Custom Trading Strategy
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from bot.strategies.base_strategy import BaseStrategy
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class MyCustomStrategy(BaseStrategy):
    """
    Custom strategy description here.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Load parameters
        self.lookback = self.parameters.get('lookback_period', 20)
        self.threshold = self.parameters.get('threshold', 0.02)
        
        logger.info(f"MyCustomStrategy initialized with lookback={self.lookback}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate custom indicators"""
        df = data.copy()
        
        # Example: Calculate custom indicators
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(self.lookback).std()
        df['momentum'] = df['close'].pct_change(self.lookback)
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate trading signal"""
        df = self.calculate_indicators(data)
        
        # Need enough data
        if len(df) < self.lookback:
            return 'HOLD'
        
        # Get latest values
        current_momentum = df['momentum'].iloc[-1]
        current_volatility = df['volatility'].iloc[-1]
        
        # Check for NaN
        if pd.isna(current_momentum) or pd.isna(current_volatility):
            return 'HOLD'
        
        # Custom signal logic
        if current_momentum > self.threshold and current_volatility < 0.05:
            logger.info(f"BUY signal: momentum={current_momentum:.4f}")
            return 'BUY'
        elif current_momentum < -self.threshold:
            logger.info(f"SELL signal: momentum={current_momentum:.4f}")
            return 'SELL'
        
        return 'HOLD'
```

### Step 3: Create Configuration

Add configuration in `config/strategies/strategy_config.json`:

```json
{
    "my_custom": {
        "enabled": true,
        "parameters": {
            "lookback_period": 20,
            "threshold": 0.02,
            "symbol": "BTC/USDT"
        },
        "risk_settings": {
            "position_size": 100,
            "stop_loss_pct": 2.0,
            "take_profit_pct": 5.0
        }
    }
}
```

### Step 4: Register Strategy

Add import in `user_strategies/__init__.py`:

```python
from .my_custom_strategy import MyCustomStrategy

__all__ = ['MyCustomStrategy']
```

### Step 5: Test Strategy

```python
from user_strategies.my_custom_strategy import MyCustomStrategy
import pandas as pd

# Create test data
test_data = pd.DataFrame({
    'open': [100, 101, 102, 103],
    'high': [102, 103, 104, 105],
    'low': [99, 100, 101, 102],
    'close': [101, 102, 103, 104],
    'volume': [1000, 1100, 1200, 1300]
})

# Initialize strategy
config = {
    "parameters": {"lookback_period": 2, "threshold": 0.01},
    "risk_settings": {"stop_loss_pct": 2.0}
}

strategy = MyCustomStrategy(config)
signal = strategy.generate_signal(test_data)
print(f"Signal: {signal}")
```

---

## Technical Indicators Reference

The bot includes TA-Lib for technical analysis. Here are commonly used indicators:

### Trend Indicators

#### Simple Moving Average (SMA)
```python
import talib

df['sma'] = talib.SMA(df['close'], timeperiod=20)
```

#### Exponential Moving Average (EMA)
```python
df['ema'] = talib.EMA(df['close'], timeperiod=20)
```

#### MACD
```python
macd, signal, hist = talib.MACD(df['close'], 
                                 fastperiod=12, 
                                 slowperiod=26, 
                                 signalperiod=9)
df['macd'] = macd
df['macd_signal'] = signal
df['macd_hist'] = hist
```

### Momentum Indicators

#### RSI (Relative Strength Index)
```python
df['rsi'] = talib.RSI(df['close'], timeperiod=14)
```

#### Stochastic Oscillator
```python
slowk, slowd = talib.STOCH(df['high'], df['low'], df['close'],
                           fastk_period=14,
                           slowk_period=3,
                           slowd_period=3)
df['stoch_k'] = slowk
df['stoch_d'] = slowd
```

#### CCI (Commodity Channel Index)
```python
df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
```

### Volatility Indicators

#### Bollinger Bands
```python
upper, middle, lower = talib.BBANDS(df['close'],
                                     timeperiod=20,
                                     nbdevup=2,
                                     nbdevdn=2)
df['bb_upper'] = upper
df['bb_middle'] = middle
df['bb_lower'] = lower
```

#### ATR (Average True Range)
```python
df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
```

### Volume Indicators

#### OBV (On-Balance Volume)
```python
df['obv'] = talib.OBV(df['close'], df['volume'])
```

#### AD (Accumulation/Distribution)
```python
df['ad'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])
```

### Pattern Recognition

```python
# Doji pattern
df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])

# Hammer
df['hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])

# Engulfing pattern
df['engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
```

### Custom Indicators (Pandas)

```python
# Rate of Change
df['roc'] = df['close'].pct_change(periods=10) * 100

# Standard Deviation
df['std'] = df['close'].rolling(window=20).std()

# Z-Score
df['zscore'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()

# VWAP (Volume Weighted Average Price)
df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
```

---

## Strategy Configuration

### Configuration File Structure

Located in `config/strategies/strategy_config.json`:

```json
{
    "active_strategies": ["sma_crossover", "rsi_bb"],
    "strategies": {
        "strategy_name": {
            "enabled": true,
            "parameters": {
                "param1": value1,
                "param2": value2
            },
            "risk_settings": {
                "position_size": 100,
                "stop_loss_pct": 2.0,
                "take_profit_pct": 5.0
            }
        }
    },
    "backtest_settings": {
        "initial_capital": 10000,
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "commission": 0.001
    }
}
```

### Parameters Section

Strategy-specific parameters:

```json
"parameters": {
    "fast_period": 10,
    "slow_period": 30,
    "symbol": "BTC/USDT",
    "timeframe": "1h"
}
```

### Risk Settings Section

Risk management configuration:

```json
"risk_settings": {
    "position_size": 100,          // Position size in base currency
    "stop_loss_pct": 2.0,          // Stop loss percentage
    "take_profit_pct": 5.0,        // Take profit percentage
    "max_positions": 3,            // Max concurrent positions
    "trailing_stop": false,        // Enable trailing stop
    "trailing_stop_pct": 1.0       // Trailing stop percentage
}
```

### Multiple Strategies

Configure multiple strategies to run simultaneously:

```json
{
    "active_strategies": ["strategy1", "strategy2", "strategy3"],
    "strategies": {
        "strategy1": {
            "enabled": true,
            "parameters": {"symbol": "BTC/USDT"}
        },
        "strategy2": {
            "enabled": true,
            "parameters": {"symbol": "ETH/USDT"}
        },
        "strategy3": {
            "enabled": false,
            "parameters": {"symbol": "SOL/USDT"}
        }
    }
}
```

---

## Backtesting Guide

### Overview

Backtesting allows you to test your strategy on historical data before risking real capital.

### Setting Up Backtesting

1. **Configure Backtest Settings**

```json
"backtest_settings": {
    "initial_capital": 10000,
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "commission": 0.001,
    "slippage": 0.0005
}
```

2. **Prepare Historical Data**

Ensure you have historical OHLCV data for your symbols.

3. **Run Backtest**

```python
from bot.core.backtester import Backtester
from user_strategies.my_strategy import MyStrategy

# Initialize backtester
backtester = Backtester(
    strategy_class=MyStrategy,
    config=strategy_config,
    start_date='2023-01-01',
    end_date='2024-01-01',
    initial_capital=10000
)

# Run backtest
results = backtester.run()

# View results
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
```

### Performance Metrics

Key metrics to evaluate:

- **Total Return:** Overall profit/loss percentage
- **Sharpe Ratio:** Risk-adjusted return (>1 is good, >2 is excellent)
- **Max Drawdown:** Largest peak-to-trough decline
- **Win Rate:** Percentage of winning trades
- **Profit Factor:** Gross profit / Gross loss
- **Average Win/Loss:** Average profit per winning/losing trade

### Analyzing Results

```python
# Plot equity curve
results.plot_equity_curve()

# Plot trades
results.plot_trades()

# View trade log
print(results.trades_df)

# Export results
results.to_csv('backtest_results.csv')
```

### Optimization

Optimize strategy parameters:

```python
from bot.core.optimizer import StrategyOptimizer

optimizer = StrategyOptimizer(
    strategy_class=MyStrategy,
    param_grid={
        'lookback_period': [10, 20, 30, 50],
        'threshold': [0.01, 0.02, 0.03, 0.05]
    }
)

# Run optimization
best_params = optimizer.optimize(
    metric='sharpe_ratio',
    method='grid_search'
)

print(f"Best parameters: {best_params}")
```

---

## Risk Management

### Position Sizing

#### Fixed Size
```python
"risk_settings": {
    "position_size": 1000,  // Fixed $1000 per trade
    "position_size_type": "fixed"
}
```

#### Percentage of Capital
```python
"risk_settings": {
    "position_size_pct": 10,  // 10% of portfolio
    "position_size_type": "percentage"
}
```

#### Risk-Based (Kelly Criterion)
```python
"risk_settings": {
    "risk_per_trade": 1,  // Risk 1% per trade
    "position_size_type": "risk_based"
}
```

### Stop Loss

#### Percentage-Based
```python
"risk_settings": {
    "stop_loss_pct": 2.0,  // 2% stop loss
    "stop_loss_type": "percentage"
}
```

#### ATR-Based
```python
"risk_settings": {
    "stop_loss_atr_multiplier": 2.0,
    "stop_loss_type": "atr"
}
```

#### Trailing Stop
```python
"risk_settings": {
    "trailing_stop": true,
    "trailing_stop_pct": 1.0
}
```

### Take Profit

```python
"risk_settings": {
    "take_profit_pct": 5.0,
    "take_profit_levels": [2.0, 3.5, 5.0],  // Multiple levels
    "take_profit_percentages": [30, 40, 30]  // % to close at each level
}
```

### Portfolio Risk Management

Global risk settings in `config/global.json`:

```json
"risk_management": {
    "max_position_size": 1000,
    "max_daily_loss": 500,
    "max_open_positions": 5,
    "max_exposure": 0.5,           // Max 50% portfolio exposure
    "position_correlation_limit": 0.7,
    "emergency_stop_loss": 10.0    // Emergency stop at 10% loss
}
```

---

## Best Practices

### 1. Data Validation

Always validate data before processing:

```python
def generate_signal(self, data: pd.DataFrame) -> str:
    # Check minimum data length
    if len(data) < self.min_periods:
        logger.warning(f"Insufficient data: {len(data)} < {self.min_periods}")
        return 'HOLD'
    
    df = self.calculate_indicators(data)
    
    # Check for NaN values
    if df[['indicator1', 'indicator2']].iloc[-1].isna().any():
        logger.warning("NaN values detected in indicators")
        return 'HOLD'
    
    # Continue with signal generation
    ...
```

### 2. Logging

Use comprehensive logging:

```python
from bot.utils.logger import get_logger

logger = get_logger(__name__)

# Log important events
logger.info(f"BUY signal generated: price={price}, indicator={value}")
logger.warning(f"Unusual volatility detected: {volatility}")
logger.error(f"Calculation error: {error}")
```

### 3. Error Handling

Implement robust error handling:

```python
def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    try:
        df = data.copy()
        df['indicator'] = self._calculate_indicator(df)
        return df
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}", exc_info=True)
        return data  # Return original data on error
```

### 4. Parameter Validation

Validate parameters on initialization:

```python
def __init__(self, config: Dict[str, Any]):
    super().__init__(config)
    
    # Validate parameters
    self.period = self.parameters.get('period', 20)
    if self.period < 1:
        raise ValueError("Period must be positive")
    
    self.threshold = self.parameters.get('threshold', 0.02)
    if not 0 < self.threshold < 1:
        raise ValueError("Threshold must be between 0 and 1")
```

### 5. Testing

Write unit tests for your strategies:

```python
import unittest
from user_strategies.my_strategy import MyStrategy

class TestMyStrategy(unittest.TestCase):
    def setUp(self):
        self.config = {
            "parameters": {"period": 20},
            "risk_settings": {"stop_loss_pct": 2.0}
        }
        self.strategy = MyStrategy(self.config)
    
    def test_signal_generation(self):
        test_data = self._create_test_data()
        signal = self.strategy.generate_signal(test_data)
        self.assertIn(signal, ['BUY', 'SELL', 'HOLD'])
    
    def test_indicator_calculation(self):
        test_data = self._create_test_data()
        df = self.strategy.calculate_indicators(test_data)
        self.assertIn('my_indicator', df.columns)
```

### 6. Performance Optimization

- Use vectorized operations (Pandas/NumPy) instead of loops
- Cache expensive calculations
- Limit data lookback to necessary periods

```python
# Good: Vectorized
df['returns'] = df['close'].pct_change()

# Bad: Loop
returns = []
for i in range(1, len(df)):
    ret = (df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]
    returns.append(ret)
```

### 7. Documentation

Document your strategy thoroughly:

```python
class MyStrategy(BaseStrategy):
    """
    Custom Momentum Strategy
    
    This strategy identifies momentum breakouts using a combination
    of price rate-of-change and volume analysis.
    
    Entry Signals:
        - BUY: Price momentum > threshold AND volume > average volume
        - SELL: Price momentum < -threshold
    
    Exit Signals:
        - Stop Loss: 2% below entry
        - Take Profit: 5% above entry
    
    Parameters:
        lookback_period (int): Period for momentum calculation (default: 20)
        threshold (float): Momentum threshold for signals (default: 0.02)
        volume_multiplier (float): Volume threshold multiplier (default: 1.5)
    
    Best Used For:
        - Trending markets with clear momentum
        - Medium-term trading (hours to days)
        - High liquidity instruments
    
    Example:
        >>> config = {
        ...     "parameters": {
        ...         "lookback_period": 20,
        ...         "threshold": 0.02
        ...     }
        ... }
        >>> strategy = MyStrategy(config)
        >>> signal = strategy.generate_signal(data)
    """
```

---

## Advanced Topics

### Multi-Timeframe Analysis

Analyze multiple timeframes simultaneously:

```python
class MultiTimeframeStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.timeframes = ['1h', '4h', '1d']
    
    def generate_signal(self, data: Dict[str, pd.DataFrame]) -> str:
        """
        data: Dictionary of {timeframe: DataFrame}
        """
        # Analyze 1-hour trend
        short_term_signal = self._analyze_timeframe(data['1h'], short=True)
        
        # Analyze 4-hour trend
        medium_term_signal = self._analyze_timeframe(data['4h'])
        
        # Analyze daily trend
        long_term_signal = self._analyze_timeframe(data['1d'], long=True)
        
        # Combine signals
        if all([short_term_signal == 'BUY',
                medium_term_signal == 'BUY',
                long_term_signal == 'BUY']):
            return 'BUY'
        
        return 'HOLD'
```

### Machine Learning Integration

Integrate ML models into strategies:

```python
import joblib
from sklearn.ensemble import RandomForestClassifier

class MLStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        # Load pre-trained model
        self.model = joblib.load('models/my_model.pkl')
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Feature engineering
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(20).std()
        df['rsi'] = talib.RSI(df['close'])
        # ... more features
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        df = self.calculate_indicators(data)
        
        # Prepare features
        features = df[['returns', 'volatility', 'rsi']].iloc[-1].values
        
        # Predict
        prediction = self.model.predict([features])[0]
        
        if prediction == 1:
            return 'BUY'
        elif prediction == -1:
            return 'SELL'
        
        return 'HOLD'
```

### Portfolio Strategies

Manage multiple assets:

```python
class PortfolioStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.symbols = config['parameters']['symbols']
        self.allocations = {}
    
    def analyze_portfolio(self, data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Analyze multiple symbols and return signals for each
        """
        signals = {}
        
        for symbol in self.symbols:
            if symbol in data:
                signal = self._analyze_symbol(data[symbol])
                signals[symbol] = signal
        
        return signals
    
    def rebalance_portfolio(self):
        """Calculate optimal portfolio weights"""
        # Implement portfolio optimization logic
        pass
```

### Custom Risk Management

Implement advanced risk management:

```python
class AdvancedRiskStrategy(BaseStrategy):
    def calculate_position_size(self, price: float, volatility: float) -> float:
        """
        Calculate position size based on volatility and risk tolerance
        """
        account_balance = self.get_account_balance()
        risk_per_trade = account_balance * 0.01  # Risk 1% per trade
        
        # ATR-based stop distance
        stop_distance = volatility * 2
        
        # Position size = Risk / Stop Distance
        position_size = risk_per_trade / stop_distance
        
        return min(position_size, self.risk_settings['max_position_size'])
    
    def adjust_stop_loss(self, current_price: float, entry_price: float):
        """
        Implement trailing stop loss
        """
        if self.position == 'LONG':
            profit_pct = (current_price - entry_price) / entry_price
            
            if profit_pct > 0.05:  # 5% profit
                # Trail stop to breakeven + 2%
                new_stop = entry_price * 1.02
                self.update_stop_loss(new_stop)
```

---

## Complete Examples

### Example 1: Volume-Weighted Momentum Strategy

```python
"""
Volume-Weighted Momentum Strategy
Trades based on price momentum confirmed by volume
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from bot.strategies.base_strategy import BaseStrategy
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class VolumeWeightedMomentum(BaseStrategy):
    """
    Generates signals when price momentum is confirmed by volume.
    
    BUY: Strong positive momentum + above-average volume
    SELL: Strong negative momentum or exit conditions met
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.momentum_period = self.parameters.get('momentum_period', 20)
        self.volume_period = self.parameters.get('volume_period', 20)
        self.momentum_threshold = self.parameters.get('momentum_threshold', 0.03)
        self.volume_multiplier = self.parameters.get('volume_multiplier', 1.5)
        
        logger.info(f"VolumeWeightedMomentum initialized: "
                   f"momentum={self.momentum_period}, "
                   f"volume={self.volume_period}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum and volume indicators"""
        df = data.copy()
        
        # Price momentum
        df['momentum'] = df['close'].pct_change(self.momentum_period)
        
        # Volume analysis
        df['avg_volume'] = df['volume'].rolling(self.volume_period).mean()
        df['volume_ratio'] = df['volume'] / df['avg_volume']
        
        # Volatility
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(self.momentum_period).std()
        
        # Trend strength
        df['sma_short'] = df['close'].rolling(10).mean()
        df['sma_long'] = df['close'].rolling(50).mean()
        df['trend'] = (df['sma_short'] > df['sma_long']).astype(int)
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate trading signal"""
        df = self.calculate_indicators(data)
        
        # Need enough data
        min_periods = max(self.momentum_period, self.volume_period, 50)
        if len(df) < min_periods:
            return 'HOLD'
        
        # Get latest values
        current_momentum = df['momentum'].iloc[-1]
        current_volume_ratio = df['volume_ratio'].iloc[-1]
        current_trend = df['trend'].iloc[-1]
        current_volatility = df['volatility'].iloc[-1]
        
        # Check for NaN
        if pd.isna(current_momentum) or pd.isna(current_volume_ratio):
            return 'HOLD'
        
        # BUY Signal: Strong momentum + high volume + uptrend
        if (current_momentum > self.momentum_threshold and
            current_volume_ratio > self.volume_multiplier and
            current_trend == 1 and
            current_volatility < 0.05):  # Not too volatile
            
            logger.info(f"BUY signal: momentum={current_momentum:.4f}, "
                       f"volume_ratio={current_volume_ratio:.2f}")
            return 'BUY'
        
        # SELL Signal: Negative momentum or exit conditions
        if current_momentum < -self.momentum_threshold:
            logger.info(f"SELL signal: negative momentum={current_momentum:.4f}")
            return 'SELL'
        
        # Exit if trend reverses
        if self.position == 'LONG' and current_trend == 0:
            logger.info("SELL signal: trend reversal")
            return 'SELL'
        
        return 'HOLD'
```

**Configuration:**
```json
{
    "volume_weighted_momentum": {
        "enabled": true,
        "parameters": {
            "momentum_period": 20,
            "volume_period": 20,
            "momentum_threshold": 0.03,
            "volume_multiplier": 1.5,
            "symbol": "BTC/USDT"
        },
        "risk_settings": {
            "position_size": 1000,
            "stop_loss_pct": 3.0,
            "take_profit_pct": 8.0
        }
    }
}
```

### Example 2: Mean Reversion Strategy

```python
"""
Bollinger Bands Mean Reversion Strategy
"""

import pandas as pd
from typing import Dict, Any
from bot.strategies.base_strategy import BaseStrategy
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy using Bollinger Bands and RSI.
    
    BUY: Price touches lower band + RSI oversold
    SELL: Price touches upper band + RSI overbought
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std = self.parameters.get('bb_std', 2.0)
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.rsi_oversold = self.parameters.get('rsi_oversold', 30)
        self.rsi_overbought = self.parameters.get('rsi_overbought', 70)
        self.bb_touch_threshold = self.parameters.get('bb_touch_threshold', 0.01)
        
        logger.info(f"MeanReversionStrategy initialized")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and RSI"""
        df = data.copy()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(self.bb_period).mean()
        bb_std = df['close'].rolling(self.bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * self.bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std * self.bb_std)
        
        # BB width and position
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(self.rsi_period).mean()
        loss = -delta.where(delta < 0, 0).rolling(self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate mean reversion signal"""
        df = self.calculate_indicators(data)
        
        min_periods = max(self.bb_period, self.rsi_period)
        if len(df) < min_periods:
            return 'HOLD'
        
        current_close = df['close'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        bb_middle = df['bb_middle'].iloc[-1]
        bb_position = df['bb_position'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        bb_width = df['bb_width'].iloc[-1]
        
        if pd.isna(rsi) or pd.isna(bb_position):
            return 'HOLD'
        
        # Only trade when bands are not too narrow (avoid low volatility)
        if bb_width < 0.02:
            return 'HOLD'
        
        # BUY: Price near lower band + oversold RSI
        if (bb_position < self.bb_touch_threshold and 
            rsi < self.rsi_oversold):
            logger.info(f"BUY signal: price near lower BB, RSI={rsi:.2f}")
            return 'BUY'
        
        # SELL: Price near upper band + overbought RSI
        if (bb_position > (1 - self.bb_touch_threshold) and 
            rsi > self.rsi_overbought):
            logger.info(f"SELL signal: price near upper BB, RSI={rsi:.2f}")
            return 'SELL'
        
        # Exit long position when price reaches middle band
        if self.position == 'LONG' and current_close >= bb_middle:
            logger.info("SELL signal: price reached middle band")
            return 'SELL'
        
        return 'HOLD'
```

---

## Troubleshooting

### Common Issues

#### 1. "Insufficient data" warnings

**Cause:** Not enough historical data for indicator calculation

**Solution:**
```python
# Increase lookback period in config
"data": {
    "lookback_period": 200  # Increase from 100
}

# Or check minimum data in strategy
min_required = max(self.period1, self.period2, self.period3)
if len(data) < min_required:
    return 'HOLD'
```

#### 2. NaN values in indicators

**Cause:** Insufficient data or calculation errors

**Solution:**
```python
# Always check for NaN
if df[['indicator1', 'indicator2']].iloc[-1].isna().any():
    logger.warning("NaN detected")
    return 'HOLD'

# Use fillna() for some indicators
df['indicator'].fillna(method='ffill', inplace=True)
```

#### 3. Strategy not generating signals

**Debug steps:**
```python
# Add debug logging
logger.debug(f"Data shape: {data.shape}")
logger.debug(f"Latest close: {data['close'].iloc[-1]}")
logger.debug(f"Indicator value: {indicator_value}")

# Check signal conditions
logger.debug(f"Condition 1: {condition1}")
logger.debug(f"Condition 2: {condition2}")
```

#### 4. Performance issues

**Solutions:**
- Use vectorized operations instead of loops
- Reduce indicator calculation complexity
- Limit data lookback period
- Cache expensive calculations

```python
# Cache indicators
@functools.lru_cache(maxsize=128)
def _calculate_expensive_indicator(self, data_hash):
    # Expensive calculation
    pass
```

#### 5. Import errors

**Solution:**
```python
# Ensure proper imports
from bot.strategies.base_strategy import BaseStrategy
from bot.utils.logger import get_logger

# Check __init__.py files exist
# Check PYTHONPATH includes project root
```

### Getting Help

1. **Check logs:** `logs/trading_bot.log`
2. **Enable debug logging:** Set `LOG_LEVEL=DEBUG` in `.env`
3. **Run tests:** `pytest tests/test_strategies.py`
4. **Review documentation:** This guide and API reference

### Performance Tips

1. **Optimize indicator calculations** - Use TA-Lib when possible
2. **Limit data lookback** - Only request necessary data
3. **Avoid lookahead bias** - Never use future data in calculations
4. **Test thoroughly** - Backtest on different market conditions
5. **Monitor in paper trading** - Test in paper mode before live trading

---

## Conclusion

This guide covered everything needed to develop, test, and deploy trading strategies. Remember:

- Start simple and iterate
- Always backtest before live trading
- Implement proper risk management
- Monitor and adjust strategies regularly
- Keep learning and improving

For additional help:
- See [API_REFERENCE.md](API_REFERENCE.md) for API documentation
- See [BROKER_SETUP.md](BROKER_SETUP.md) for broker configuration
- See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options

Happy trading! 🚀
