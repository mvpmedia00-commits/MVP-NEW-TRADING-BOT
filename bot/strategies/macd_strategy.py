"""
MACD Strategy
"""

import pandas as pd
from typing import Dict, Any

from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MACDStrategy(BaseStrategy):
    """
    MACD (Moving Average Convergence Divergence) Strategy
    
    Generates BUY signal when MACD line crosses above signal line
    Generates SELL signal when MACD line crosses below signal line
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MACD strategy
        
        Args:
            config: Strategy configuration with parameters:
                - fast_period: Fast EMA period (default: 12)
                - slow_period: Slow EMA period (default: 26)
                - signal_period: Signal line period (default: 9)
        """
        super().__init__(config)
        self.fast_period = self.parameters.get('fast_period', 12)
        self.slow_period = self.parameters.get('slow_period', 26)
        self.signal_period = self.parameters.get('signal_period', 9)
        
        logger.info(f"MACD initialized with fast={self.fast_period}, slow={self.slow_period}, signal={self.signal_period}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD indicators
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added MACD columns
        """
        df = data.copy()
        
        # Calculate EMAs
        ema_fast = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate MACD line
        df['macd'] = ema_fast - ema_slow
        
        # Calculate signal line
        df['macd_signal'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # Calculate MACD histogram
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Calculate previous values for crossover detection
        df['macd_histogram_prev'] = df['macd_histogram'].shift(1)
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate trading signal based on MACD
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        df = self.calculate_indicators(data)
        
        min_periods = self.slow_period + self.signal_period
        if len(df) < min_periods:
            logger.warning(f"Insufficient data: {len(df)} < {min_periods}")
            return 'HOLD'
        
        # Get latest values
        current_histogram = df['macd_histogram'].iloc[-1]
        prev_histogram = df['macd_histogram_prev'].iloc[-1]
        current_macd = df['macd'].iloc[-1]
        current_signal = df['macd_signal'].iloc[-1]
        
        # Check for NaN values
        if pd.isna(current_histogram) or pd.isna(prev_histogram):
            return 'HOLD'
        
        # Bullish crossover: MACD crosses above signal line
        if prev_histogram <= 0 and current_histogram > 0:
            logger.info(f"BUY signal: MACD crossed above signal line (MACD={current_macd:.2f}, Signal={current_signal:.2f})")
            return 'BUY'
        
        # Bearish crossover: MACD crosses below signal line
        if prev_histogram >= 0 and current_histogram < 0:
            logger.info(f"SELL signal: MACD crossed below signal line (MACD={current_macd:.2f}, Signal={current_signal:.2f})")
            return 'SELL'
        
        return 'HOLD'
