"""
RSI + Bollinger Bands Strategy
"""

import pandas as pd
from typing import Dict, Any

from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RSIBBStrategy(BaseStrategy):
    """
    RSI + Bollinger Bands Strategy
    
    Generates BUY signal when RSI is oversold and price is near lower BB
    Generates SELL signal when RSI is overbought and price is near upper BB
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RSI + Bollinger Bands strategy
        
        Args:
            config: Strategy configuration with parameters:
                - rsi_period: RSI calculation period (default: 14)
                - rsi_oversold: RSI oversold threshold (default: 30)
                - rsi_overbought: RSI overbought threshold (default: 70)
                - bb_period: Bollinger Bands period (default: 20)
                - bb_std: Bollinger Bands standard deviation (default: 2)
        """
        super().__init__(config)
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.rsi_oversold = self.parameters.get('rsi_oversold', 30)
        self.rsi_overbought = self.parameters.get('rsi_overbought', 70)
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std = self.parameters.get('bb_std', 2)
        
        logger.info(f"RSI+BB initialized with RSI={self.rsi_period}, BB={self.bb_period}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI and Bollinger Bands indicators
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added RSI and BB columns
        """
        df = data.copy()
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=self.bb_period).mean()
        bb_std = df['close'].rolling(window=self.bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * self.bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std * self.bb_std)
        
        # Calculate BB width percentage
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle'] * 100
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate trading signal based on RSI and Bollinger Bands
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        df = self.calculate_indicators(data)
        
        min_periods = max(self.rsi_period, self.bb_period)
        if len(df) < min_periods:
            logger.warning(f"Insufficient data: {len(df)} < {min_periods}")
            return 'HOLD'
        
        # Get latest values
        current_rsi = df['rsi'].iloc[-1]
        current_close = df['close'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        bb_middle = df['bb_middle'].iloc[-1]
        
        # Check for NaN values
        if pd.isna(current_rsi) or pd.isna(bb_upper) or pd.isna(bb_lower):
            return 'HOLD'
        
        # BUY signal: RSI oversold and price near lower BB
        if current_rsi < self.rsi_oversold and current_close < bb_lower:
            logger.info(f"BUY signal: RSI={current_rsi:.2f} oversold, price below lower BB")
            return 'BUY'
        
        # SELL signal: RSI overbought and price near upper BB
        if current_rsi > self.rsi_overbought and current_close > bb_upper:
            logger.info(f"SELL signal: RSI={current_rsi:.2f} overbought, price above upper BB")
            return 'SELL'
        
        # Additional exit signals
        if current_rsi > self.rsi_overbought or current_close > bb_middle:
            if self.position == 'LONG':
                logger.info(f"SELL signal: Exit long position")
                return 'SELL'
        
        if current_rsi < self.rsi_oversold or current_close < bb_middle:
            if self.position == 'SHORT':
                logger.info(f"BUY signal: Exit short position")
                return 'BUY'
        
        return 'HOLD'
