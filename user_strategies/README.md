# Custom Trading Strategies Guide

Welcome to the custom strategies guide for the MVP Trading Bot! This guide will help you create your own trading strategies.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Strategy Structure](#strategy-structure)
3. [Creating Your First Strategy](#creating-your-first-strategy)
4. [Strategy Configuration](#strategy-configuration)
5. [Backtesting Your Strategy](#backtesting-your-strategy)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

---

## Quick Start

1. **Copy the template:**
   ```bash
   cp user_strategies/custom_strategy_template.py user_strategies/my_strategy.py
   ```

2. **Implement your strategy logic:**
   - Define indicator calculations in `calculate_indicators()`
   - Implement signal generation in `generate_signal()`

3. **Create a configuration file:**
   ```bash
   cp config/strategies/_template.json config/strategies/my_strategy.json
   ```

4. **Backtest your strategy:**
   ```bash
   python scripts/backtest.py --strategy my_strategy --symbol BTC/USDT --days 30
   ```

5. **Enable your strategy:**
   - Edit `config/strategies.json` and add your strategy to `active_strategies`

---

## Strategy Structure

All custom strategies must inherit from `BaseStrategy` and implement these required methods:

### Required Methods

```python
def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators needed for your strategy
    
    Args:
        data: DataFrame with OHLCV data (open, high, low, close, volume)
    
    Returns:
        DataFrame with added indicator columns
    """
    pass

def generate_signal(self, data: pd.DataFrame) -> str:
    """
    Generate trading signal based on indicators
    
    Args:
        data: DataFrame with OHLCV data and indicators
    
    Returns:
        'BUY', 'SELL', or 'HOLD'
    """
    pass
```

### Inherited Methods

Your strategy automatically inherits these useful methods from `BaseStrategy`:

- `should_enter(data)` - Check if conditions are met to enter a position
- `should_exit(data, current_price)` - Check if should exit current position
- `check_stop_loss(current_price)` - Automatic stop loss checking
- `check_take_profit(current_price)` - Automatic take profit checking
- `get_position_size()` - Calculate position size based on risk settings
- `enter_position(type, price)` - Record position entry
- `exit_position()` - Record position exit

---

## Creating Your First Strategy

Let's create a simple Moving Average Crossover strategy:

```python
from bot.strategies.base_strategy import BaseStrategy
import pandas as pd

class MyMAStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        # Get parameters from config
        fast_period = self.parameters.get('fast_period', 10)
        slow_period = self.parameters.get('slow_period', 30)
        
        # Calculate moving averages
        data['ma_fast'] = data['close'].rolling(window=fast_period).mean()
        data['ma_slow'] = data['close'].rolling(window=slow_period).mean()
        
        return data
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        # Get latest values
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Check for crossover
        if current['ma_fast'] > current['ma_slow'] and previous['ma_fast'] <= previous['ma_slow']:
            return 'BUY'  # Golden cross
        elif current['ma_fast'] < current['ma_slow'] and previous['ma_fast'] >= previous['ma_slow']:
            return 'SELL'  # Death cross
        
        return 'HOLD'
```

---

## Strategy Configuration

Create a JSON configuration file in `config/strategies/`:

```json
{
  "enabled": true,
  "description": "My custom MA crossover strategy",
  "parameters": {
    "symbol": "BTC/USDT",
    "fast_period": 10,
    "slow_period": 30,
    "custom_param": "value"
  },
  "risk_settings": {
    "position_size": 100,
    "stop_loss_pct": 2.0,
    "take_profit_pct": 5.0
  }
}
```

### Configuration Parameters

- **enabled**: Enable/disable the strategy
- **description**: Human-readable description
- **parameters**: Strategy-specific parameters
  - `symbol`: Trading pair (e.g., BTC/USDT)
  - Custom parameters for your indicators
- **risk_settings**: Risk management settings
  - `position_size`: Position size in quote currency
  - `stop_loss_pct`: Stop loss percentage (e.g., 2.0 = 2%)
  - `take_profit_pct`: Take profit percentage (e.g., 5.0 = 5%)

---

## Backtesting Your Strategy

Backtesting helps you validate your strategy before risking real money:

```bash
# Backtest for last 30 days
python scripts/backtest.py --strategy my_strategy --symbol BTC/USDT --days 30

# Backtest for specific date range
python scripts/backtest.py --strategy my_strategy --symbol BTC/USDT \
  --start 2023-01-01 --end 2023-12-31

# Save results to file
python scripts/backtest.py --strategy my_strategy --symbol BTC/USDT \
  --days 90 --output results.json
```

### Interpreting Results

Key metrics to look for:

- **Win Rate**: Percentage of profitable trades (aim for >50%)
- **Profit Factor**: Gross profit / Gross loss (aim for >1.5)
- **Max Drawdown**: Maximum peak-to-trough decline (lower is better)
- **Sharpe Ratio**: Risk-adjusted return (higher is better, >1 is good)
- **Total Return**: Overall profitability

---

## Best Practices

### 1. Start Simple

Begin with simple strategies and gradually add complexity. Simple strategies are often more robust.

### 2. Use Multiple Timeframes

Consider using multiple timeframe analysis for better signal confirmation:

```python
def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    # Short-term trend
    data['ema_short'] = data['close'].ewm(span=12).mean()
    
    # Medium-term trend
    data['ema_medium'] = data['close'].ewm(span=26).mean()
    
    # Long-term trend
    data['ema_long'] = data['close'].ewm(span=50).mean()
    
    return data
```

### 3. Implement Proper Risk Management

Always use stop losses and position sizing:

```python
# In your config file
"risk_settings": {
    "position_size": 100,
    "stop_loss_pct": 2.0,      # 2% stop loss
    "take_profit_pct": 5.0      # 5% take profit
}
```

### 4. Avoid Overfitting

Don't optimize your strategy to work perfectly on historical data. It won't work on future data.

### 5. Test Multiple Market Conditions

Test your strategy in:
- Bull markets (trending up)
- Bear markets (trending down)
- Sideways/ranging markets
- High volatility periods
- Low volatility periods

### 6. Handle Edge Cases

```python
def generate_signal(self, data: pd.DataFrame) -> str:
    # Check if we have enough data
    if len(data) < 30:
        return 'HOLD'
    
    # Check for NaN values
    if data['ma_fast'].isna().any() or data['ma_slow'].isna().any():
        return 'HOLD'
    
    # Your signal logic here
    # ...
```

### 7. Log Important Events

```python
from bot.utils import get_logger

logger = get_logger(__name__)

def generate_signal(self, data: pd.DataFrame) -> str:
    signal = self._calculate_signal(data)
    
    if signal != 'HOLD':
        logger.info(f"Signal generated: {signal} at price {data.iloc[-1]['close']}")
    
    return signal
```

---

## Available Indicators

The bot includes common technical indicators via the `ta-lib` library:

### Trend Indicators
- Moving Averages: SMA, EMA, WMA
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)

### Momentum Indicators
- RSI (Relative Strength Index)
- Stochastic Oscillator
- CCI (Commodity Channel Index)

### Volatility Indicators
- Bollinger Bands
- ATR (Average True Range)

### Volume Indicators
- OBV (On-Balance Volume)
- Volume Rate of Change

### Example Usage

```python
import pandas as pd
import talib

def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    # RSI
    data['rsi'] = talib.RSI(data['close'], timeperiod=14)
    
    # Bollinger Bands
    data['bb_upper'], data['bb_middle'], data['bb_lower'] = talib.BBANDS(
        data['close'], timeperiod=20, nbdevup=2, nbdevdn=2
    )
    
    # MACD
    data['macd'], data['macd_signal'], data['macd_hist'] = talib.MACD(
        data['close'], fastperiod=12, slowperiod=26, signalperiod=9
    )
    
    return data
```

---

## Examples

See the `examples/` directory for complete strategy examples:

1. **example_strategy_1.py** - RSI + Bollinger Bands strategy
2. **example_strategy_2.py** - MACD + EMA trend following strategy

Study these examples to learn different approaches to strategy development.

---

## Troubleshooting

### Common Issues

**1. Strategy not executing trades in backtest**
- Check if indicators are calculated correctly
- Verify signal logic is not too strict
- Ensure you have enough historical data

**2. Too many trades (overtrading)**
- Add filters to reduce false signals
- Increase indicator periods
- Add confirmation from multiple indicators

**3. Poor performance**
- Backtest on different time periods
- Adjust indicator parameters
- Consider market conditions when strategy works best

**4. Import errors**
- Make sure your strategy file is in `user_strategies/`
- Check that the class name matches the file name convention
- Verify all imports are correct

---

## Advanced Topics

### Custom Risk Management

Override the inherited risk management methods:

```python
def get_position_size(self) -> float:
    """Custom position sizing based on volatility"""
    # Calculate position size based on ATR
    # Implement your logic here
    pass
```

### Multiple Symbol Support

```python
def __init__(self, config: Dict[str, Any]):
    super().__init__(config)
    self.symbols = self.parameters.get('symbols', ['BTC/USDT'])
```

### State Persistence

Save strategy state between restarts:

```python
def get_status(self) -> Dict[str, Any]:
    """Get strategy status including custom state"""
    status = super().get_status()
    status['custom_state'] = self.my_custom_variable
    return status
```

---

## Getting Help

- Check the example strategies in `examples/`
- Review the base strategy class: `bot/strategies/base_strategy.py`
- Look at built-in strategies in `bot/strategies/`
- Read the main documentation in the project README

---

## Contributing

If you've created a successful strategy you'd like to share:

1. Remove any sensitive information
2. Add comprehensive documentation
3. Include backtest results
4. Submit as an example (but keep API keys private!)

---

**Happy Trading! Remember: Always test thoroughly before using real money!**
