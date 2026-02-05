"""
EMA Strategy with Multiple EMAs
"""

import pandas as pd
from typing import Dict, Any

from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EMAStrategy(BaseStrategy):
    """
    Exponential Moving Average Strategy
    
    Uses multiple EMAs to generate signals:
    - BUY when fast EMA > medium EMA > slow EMA (bullish alignment)
    - SELL when fast EMA < medium EMA < slow EMA (bearish alignment)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize EMA strategy
        
        Args:
            config: Strategy configuration with parameters:
                - fast_period: Fast EMA period (default: 9)
                - medium_period: Medium EMA period (default: 21)
                - slow_period: Slow EMA period (default: 50)
        """
        super().__init__(config)
        self.fast_period = self.parameters.get('fast_period', 9)
        self.medium_period = self.parameters.get('medium_period', 21)
        self.slow_period = self.parameters.get('slow_period', 50)
        
        logger.info(f"EMA Strategy initialized with fast={self.fast_period}, medium={self.medium_period}, slow={self.slow_period}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate EMA indicators
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added EMA columns
        """
        df = data.copy()
        
        # Calculate EMAs
        df['ema_fast'] = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        df['ema_medium'] = df['close'].ewm(span=self.medium_period, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate EMA slopes (rate of change)
        df['ema_fast_slope'] = df['ema_fast'].diff()
        df['ema_medium_slope'] = df['ema_medium'].diff()
        df['ema_slow_slope'] = df['ema_slow'].diff()
        
        # Calculate distance from price to EMAs
        df['distance_to_fast'] = (df['close'] - df['ema_fast']) / df['ema_fast'] * 100
        df['distance_to_slow'] = (df['close'] - df['ema_slow']) / df['ema_slow'] * 100
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate trading signal based on EMA alignment
        
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
        ema_fast = df['ema_fast'].iloc[-1]
        ema_medium = df['ema_medium'].iloc[-1]
        ema_slow = df['ema_slow'].iloc[-1]
        current_close = df['close'].iloc[-1]
        
        # Get previous values for trend confirmation
        ema_fast_prev = df['ema_fast'].iloc[-2]
        ema_medium_prev = df['ema_medium'].iloc[-2]
        
        # Check for NaN values
        if pd.isna(ema_fast) or pd.isna(ema_medium) or pd.isna(ema_slow):
            return 'HOLD'
        
        # Bullish alignment: fast > medium > slow and price > fast EMA
        if ema_fast > ema_medium > ema_slow and current_close > ema_fast:
            # Check if this is a new crossover
            if ema_fast_prev <= ema_medium_prev:
                logger.info(f"BUY signal: Bullish EMA alignment (Fast={ema_fast:.2f} > Medium={ema_medium:.2f} > Slow={ema_slow:.2f})")
                return 'BUY'
        
        # Bearish alignment: fast < medium < slow and price < fast EMA
        if ema_fast < ema_medium < ema_slow and current_close < ema_fast:
            # Check if this is a new crossover
            if ema_fast_prev >= ema_medium_prev:
                logger.info(f"SELL signal: Bearish EMA alignment (Fast={ema_fast:.2f} < Medium={ema_medium:.2f} < Slow={ema_slow:.2f})")
                return 'SELL'
        
        # Additional signals based on price crossing fast EMA
        if current_close > ema_fast and ema_fast > ema_medium:
            prev_close = df['close'].iloc[-2]
            if prev_close <= ema_fast_prev:
                logger.info(f"BUY signal: Price crossed above fast EMA")
                return 'BUY'
        
        if current_close < ema_fast and ema_fast < ema_medium:
            prev_close = df['close'].iloc[-2]
            if prev_close >= ema_fast_prev:
                logger.info(f"SELL signal: Price crossed below fast EMA")
                return 'SELL'
        
        return 'HOLD'
