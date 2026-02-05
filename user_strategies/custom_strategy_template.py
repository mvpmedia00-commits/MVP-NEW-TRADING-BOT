"""
Custom Strategy Template

This is a template for creating your own custom trading strategies.
Copy this file and implement your strategy logic.

Usage:
    1. Copy this file to create your strategy:
       cp user_strategies/custom_strategy_template.py user_strategies/my_strategy.py
    
    2. Rename the class to match your strategy name
    
    3. Implement calculate_indicators() and generate_signal()
    
    4. Create a configuration file in config/strategies/
    
    5. Test with backtesting before using in production

Author: Your Name
Created: YYYY-MM-DD
"""

import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.strategies.base_strategy import BaseStrategy
from bot.utils import get_logger

logger = get_logger(__name__)


class CustomStrategyTemplate(BaseStrategy):
    """
    Template for custom trading strategies
    
    Replace this docstring with a description of your strategy:
    - What indicators does it use?
    - What market conditions is it designed for?
    - What is the entry/exit logic?
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            config: Strategy configuration dictionary
        """
        super().__init__(config)
        
        # Extract your custom parameters here
        # These come from your strategy config JSON file
        self.example_param = self.parameters.get('example_param', 14)
        self.threshold = self.parameters.get('threshold', 0.5)
        
        logger.info(f"Initialized {self.name} with parameters: {self.parameters}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators needed for the strategy
        
        This method is called before generate_signal() to prepare
        all necessary indicators for decision making.
        
        Args:
            data: DataFrame with OHLCV data (columns: open, high, low, close, volume)
        
        Returns:
            DataFrame with added indicator columns
        
        Example indicators you might calculate:
            - Moving averages (SMA, EMA)
            - RSI (Relative Strength Index)
            - MACD (Moving Average Convergence Divergence)
            - Bollinger Bands
            - Custom indicators
        """
        # Example: Calculate a simple moving average
        # Replace this with your own indicator calculations
        
        # Simple Moving Average
        sma_period = self.parameters.get('sma_period', 20)
        data['sma'] = data['close'].rolling(window=sma_period).mean()
        
        # Exponential Moving Average
        ema_period = self.parameters.get('ema_period', 12)
        data['ema'] = data['close'].ewm(span=ema_period, adjust=False).mean()
        
        # Example: Calculate RSI (if you have talib installed)
        # import talib
        # data['rsi'] = talib.RSI(data['close'], timeperiod=14)
        
        # Example: Calculate your custom indicator
        # data['custom_indicator'] = self._calculate_custom_indicator(data)
        
        return data
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate trading signal based on market data and indicators
        
        This is the core of your strategy logic. Based on the indicators
        calculated in calculate_indicators(), decide whether to BUY, SELL,
        or HOLD.
        
        Args:
            data: DataFrame with OHLCV data and calculated indicators
        
        Returns:
            'BUY'  - Enter a long position
            'SELL' - Enter a short position (or exit long)
            'HOLD' - Do nothing
        
        Tips:
            - Use data.iloc[-1] for the current candle
            - Use data.iloc[-2] for the previous candle
            - Check for crossovers, breakouts, divergences, etc.
            - Combine multiple indicators for confirmation
        """
        # Ensure we have enough data
        if len(data) < 20:
            return 'HOLD'
        
        # Get the latest values
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Example signal logic - REPLACE THIS WITH YOUR OWN LOGIC
        # This is just a simple example and not a real trading strategy!
        
        # Buy signal example: Price crosses above SMA
        if current['close'] > current['sma'] and previous['close'] <= previous['sma']:
            logger.info(f"BUY signal: Price crossed above SMA")
            return 'BUY'
        
        # Sell signal example: Price crosses below SMA
        elif current['close'] < current['sma'] and previous['close'] >= previous['sma']:
            logger.info(f"SELL signal: Price crossed below SMA")
            return 'SELL'
        
        # No clear signal
        return 'HOLD'
    
    # Optional: Override inherited methods for custom behavior
    
    def should_enter(self, data: pd.DataFrame) -> bool:
        """
        Optional: Override to add custom entry logic beyond the signal
        
        By default, this checks if we have no position and generate_signal()
        returns BUY or SELL. You can override this to add additional filters.
        """
        # Call parent implementation
        if not super().should_enter(data):
            return False
        
        # Add your custom entry filters here
        # Example: Only enter during high volume
        # current_volume = data.iloc[-1]['volume']
        # avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        # if current_volume < avg_volume:
        #     return False
        
        return True
    
    def should_exit(self, data: pd.DataFrame, current_price: float) -> bool:
        """
        Optional: Override to add custom exit logic beyond stop loss/take profit
        
        By default, this checks stop loss, take profit, and opposing signals.
        You can override to add additional exit conditions.
        """
        # Call parent implementation for stop loss and take profit
        if super().should_exit(data, current_price):
            return True
        
        # Add your custom exit conditions here
        # Example: Exit if RSI reaches extreme levels
        # current = data.iloc[-1]
        # if 'rsi' in current:
        #     if current['rsi'] > 80 or current['rsi'] < 20:
        #         logger.info(f"Exit signal: Extreme RSI level {current['rsi']}")
        #         return True
        
        return False
    
    # Custom helper methods - add your own!
    
    def _calculate_custom_indicator(self, data: pd.DataFrame) -> pd.Series:
        """
        Example custom indicator calculation
        
        Replace this with your own custom indicator logic
        """
        # Example: Simple momentum indicator
        period = self.example_param
        return data['close'].pct_change(period)
    
    def _is_market_condition_favorable(self, data: pd.DataFrame) -> bool:
        """
        Example method to check if market conditions are favorable
        
        You might want to avoid trading in certain market conditions:
        - Low liquidity
        - High volatility
        - Sideways markets (for trend strategies)
        - Trending markets (for mean reversion strategies)
        """
        # Example: Check if market has enough volatility
        # returns = data['close'].pct_change()
        # volatility = returns.std()
        # return volatility > self.threshold
        
        return True


# Example of how to test your strategy standalone
if __name__ == '__main__':
    """
    Test your strategy with sample data
    
    This is useful for debugging your strategy logic
    """
    # Create sample OHLCV data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='1h')
    sample_data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # Create test configuration
    test_config = {
        'enabled': True,
        'parameters': {
            'symbol': 'BTC/USDT',
            'sma_period': 20,
            'ema_period': 12,
            'example_param': 14
        },
        'risk_settings': {
            'position_size': 100,
            'stop_loss_pct': 2.0,
            'take_profit_pct': 5.0
        }
    }
    
    # Initialize strategy
    strategy = CustomStrategyTemplate(test_config)
    
    # Calculate indicators
    sample_data = strategy.calculate_indicators(sample_data)
    
    # Generate signals
    for i in range(20, len(sample_data)):
        current_data = sample_data.iloc[:i+1]
        signal = strategy.generate_signal(current_data)
        
        if signal != 'HOLD':
            print(f"[{current_data.index[-1]}] Signal: {signal} at price {current_data.iloc[-1]['close']:.2f}")
    
    print("\nStrategy test complete!")
