"""
SMA Crossover Strategy
"""

import pandas as pd
from typing import Dict, Any

from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy
    
    Generates BUY signal when fast SMA crosses above slow SMA
    Generates SELL signal when fast SMA crosses below slow SMA
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SMA Crossover strategy
        
        Args:
            config: Strategy configuration with parameters:
                - fast_period: Period for fast SMA (default: 10)
                - slow_period: Period for slow SMA (default: 30)
        """
        super().__init__(config)
        self.fast_period = self.parameters.get('fast_period', 10)
        self.slow_period = self.parameters.get('slow_period', 30)
        
        logger.info(f"SMA Crossover initialized with fast={self.fast_period}, slow={self.slow_period}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMA indicators
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added SMA columns
        """
        df = data.copy()
        
        # Calculate SMAs
        df['sma_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df['sma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Calculate crossover signals
        df['sma_diff'] = df['sma_fast'] - df['sma_slow']
        df['sma_diff_prev'] = df['sma_diff'].shift(1)
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate trading signal based on SMA crossover
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        df = self.calculate_indicators(data)
        
        if len(df) < self.slow_period:
            logger.warning(f"Insufficient data: {len(df)} < {self.slow_period}")
            return 'HOLD'
        
        # Get latest values
        current_diff = df['sma_diff'].iloc[-1]
        prev_diff = df['sma_diff_prev'].iloc[-1]
        
        # Check for NaN values
        if pd.isna(current_diff) or pd.isna(prev_diff):
            return 'HOLD'
        
        # Bullish crossover: fast SMA crosses above slow SMA
        if prev_diff <= 0 and current_diff > 0:
            logger.info(f"BUY signal: Fast SMA crossed above Slow SMA")
            return 'BUY'
        
        # Bearish crossover: fast SMA crosses below slow SMA
        if prev_diff >= 0 and current_diff < 0:
            logger.info(f"SELL signal: Fast SMA crossed below Slow SMA")
            return 'SELL'
        
        return 'HOLD'
