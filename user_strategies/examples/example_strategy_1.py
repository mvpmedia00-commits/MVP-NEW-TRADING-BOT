"""
Example Strategy 1: RSI + Bollinger Bands Mean Reversion

This strategy combines RSI (Relative Strength Index) and Bollinger Bands
to identify oversold/overbought conditions for mean reversion trading.

Strategy Logic:
    BUY when:
        - RSI < 30 (oversold)
        - Price touches or breaks below lower Bollinger Band
        
    SELL when:
        - RSI > 70 (overbought)
        - Price touches or breaks above upper Bollinger Band

Market Conditions:
    - Best in ranging/sideways markets
    - Avoid using in strong trending markets
    - Works well with moderate volatility

Author: MVP Trading Bot Team
Created: 2024
"""

import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bot.strategies.base_strategy import BaseStrategy
from bot.utils import get_logger

logger = get_logger(__name__)


class RSIBollingerBands(BaseStrategy):
    """RSI + Bollinger Bands Mean Reversion Strategy"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the strategy"""
        super().__init__(config)
        
        # Strategy parameters
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.rsi_oversold = self.parameters.get('rsi_oversold', 30)
        self.rsi_overbought = self.parameters.get('rsi_overbought', 70)
        
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std_dev = self.parameters.get('bb_std_dev', 2.0)
        
        # Additional filters
        self.volume_filter = self.parameters.get('volume_filter', True)
        self.volume_period = self.parameters.get('volume_period', 20)
        
        logger.info(f"RSI-BB Strategy initialized: RSI({self.rsi_period}), BB({self.bb_period}, {self.bb_std_dev})")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI and Bollinger Bands indicators"""
        
        # Calculate RSI
        data['rsi'] = self._calculate_rsi(data['close'], self.rsi_period)
        
        # Calculate Bollinger Bands
        data['bb_middle'] = data['close'].rolling(window=self.bb_period).mean()
        bb_std = data['close'].rolling(window=self.bb_period).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * self.bb_std_dev)
        data['bb_lower'] = data['bb_middle'] - (bb_std * self.bb_std_dev)
        
        # Calculate Bollinger Band width (for volatility assessment)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        
        # Calculate volume indicators if filter is enabled
        if self.volume_filter:
            data['volume_sma'] = data['volume'].rolling(window=self.volume_period).mean()
            data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        # Calculate price position within bands (0 = lower band, 1 = upper band)
        data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])
        
        return data
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate trading signal based on RSI and Bollinger Bands"""
        
        # Need enough data for indicators
        if len(data) < max(self.rsi_period, self.bb_period) + 1:
            return 'HOLD'
        
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Check for NaN values
        required_indicators = ['rsi', 'bb_upper', 'bb_lower', 'bb_position']
        if any(pd.isna(current[ind]) for ind in required_indicators):
            return 'HOLD'
        
        # Volume filter (if enabled)
        if self.volume_filter:
            if current['volume_ratio'] < 0.5:  # Very low volume
                logger.debug("Low volume - no signal")
                return 'HOLD'
        
        # BUY Signal: Oversold conditions
        if (current['rsi'] < self.rsi_oversold and 
            current['close'] <= current['bb_lower']):
            
            # Additional confirmation: RSI starting to turn up
            if current['rsi'] > previous['rsi']:
                logger.info(f"BUY signal: RSI={current['rsi']:.2f}, Price at lower BB")
                return 'BUY'
        
        # SELL Signal: Overbought conditions
        elif (current['rsi'] > self.rsi_overbought and 
              current['close'] >= current['bb_upper']):
            
            # Additional confirmation: RSI starting to turn down
            if current['rsi'] < previous['rsi']:
                logger.info(f"SELL signal: RSI={current['rsi']:.2f}, Price at upper BB")
                return 'SELL'
        
        return 'HOLD'
    
    def should_exit(self, data: pd.DataFrame, current_price: float) -> bool:
        """Custom exit logic for mean reversion"""
        
        # Check default exit conditions (stop loss, take profit)
        if super().should_exit(data, current_price):
            return True
        
        current = data.iloc[-1]
        
        # Exit long position when price reaches middle band or RSI is neutral
        if self.position == 'LONG':
            if current['close'] >= current['bb_middle']:
                logger.info(f"Exit LONG: Price reached middle band")
                return True
            if current['rsi'] > 50:  # RSI back to neutral
                logger.info(f"Exit LONG: RSI normalized to {current['rsi']:.2f}")
                return True
        
        # Exit short position when price reaches middle band or RSI is neutral
        elif self.position == 'SHORT':
            if current['close'] <= current['bb_middle']:
                logger.info(f"Exit SHORT: Price reached middle band")
                return True
            if current['rsi'] < 50:  # RSI back to neutral
                logger.info(f"Exit SHORT: RSI normalized to {current['rsi']:.2f}")
                return True
        
        return False
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate RSI indicator
        
        Args:
            prices: Series of closing prices
            period: RSI period
            
        Returns:
            Series with RSI values
        """
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0.0)
        losses = -delta.where(delta < 0, 0.0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi


# Configuration example for this strategy
EXAMPLE_CONFIG = {
    "enabled": True,
    "description": "RSI + Bollinger Bands mean reversion strategy",
    "parameters": {
        "symbol": "BTC/USDT",
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "bb_period": 20,
        "bb_std_dev": 2.0,
        "volume_filter": True,
        "volume_period": 20
    },
    "risk_settings": {
        "position_size": 100,
        "stop_loss_pct": 3.0,
        "take_profit_pct": 5.0
    }
}


if __name__ == '__main__':
    """Test the strategy with sample data"""
    print("Testing RSI + Bollinger Bands Strategy")
    print("=" * 60)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=200, freq='1h')
    
    # Generate mean-reverting price data
    returns = np.random.randn(200) * 0.02
    prices = 100 * (1 + returns).cumprod()
    
    sample_data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(200) * 0.001),
        'high': prices * (1 + abs(np.random.randn(200)) * 0.005),
        'low': prices * (1 - abs(np.random.randn(200)) * 0.005),
        'close': prices,
        'volume': np.random.randint(1000, 10000, 200)
    }, index=dates)
    
    # Initialize strategy
    strategy = RSIBollingerBands(EXAMPLE_CONFIG)
    
    # Calculate indicators
    sample_data = strategy.calculate_indicators(sample_data)
    
    # Test signal generation
    signals = []
    for i in range(30, len(sample_data)):
        current_data = sample_data.iloc[:i+1]
        signal = strategy.generate_signal(current_data)
        
        if signal != 'HOLD':
            current = current_data.iloc[-1]
            signals.append({
                'timestamp': current_data.index[-1],
                'signal': signal,
                'price': current['close'],
                'rsi': current['rsi'],
                'bb_position': current['bb_position']
            })
    
    # Print results
    print(f"\nGenerated {len(signals)} trading signals:\n")
    for sig in signals[:10]:  # Show first 10
        print(f"{sig['timestamp']}: {sig['signal']:4s} @ ${sig['price']:7.2f} | "
              f"RSI: {sig['rsi']:5.2f} | BB Pos: {sig['bb_position']:.2f}")
    
    if len(signals) > 10:
        print(f"\n... and {len(signals) - 10} more signals")
    
    print("\n" + "=" * 60)
    print("Strategy test complete!")
