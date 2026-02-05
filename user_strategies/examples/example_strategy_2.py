"""
Example Strategy 2: MACD + EMA Trend Following

This strategy combines MACD (Moving Average Convergence Divergence) with
EMA (Exponential Moving Average) to identify and follow market trends.

Strategy Logic:
    BUY when:
        - MACD line crosses above signal line (bullish crossover)
        - Price is above the long-term EMA (uptrend confirmation)
        - MACD histogram is increasing
        
    SELL when:
        - MACD line crosses below signal line (bearish crossover)
        - Price is below the long-term EMA (downtrend confirmation)
        - MACD histogram is decreasing

Market Conditions:
    - Best in trending markets (bull or bear)
    - Avoid using in choppy/sideways markets
    - Works well with clear directional movements

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


class MACDEMATrend(BaseStrategy):
    """MACD + EMA Trend Following Strategy"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the strategy"""
        super().__init__(config)
        
        # MACD parameters
        self.macd_fast = self.parameters.get('macd_fast', 12)
        self.macd_slow = self.parameters.get('macd_slow', 26)
        self.macd_signal = self.parameters.get('macd_signal', 9)
        
        # EMA parameters
        self.ema_short = self.parameters.get('ema_short', 20)
        self.ema_long = self.parameters.get('ema_long', 50)
        
        # Additional filters
        self.use_trend_filter = self.parameters.get('use_trend_filter', True)
        self.min_histogram_value = self.parameters.get('min_histogram_value', 0.0)
        
        logger.info(f"MACD-EMA Strategy initialized: MACD({self.macd_fast},{self.macd_slow},{self.macd_signal}), "
                   f"EMA({self.ema_short},{self.ema_long})")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD and EMA indicators"""
        
        # Calculate EMAs for MACD
        ema_fast = data['close'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.macd_slow, adjust=False).mean()
        
        # Calculate MACD line and signal line
        data['macd_line'] = ema_fast - ema_slow
        data['macd_signal'] = data['macd_line'].ewm(span=self.macd_signal, adjust=False).mean()
        data['macd_histogram'] = data['macd_line'] - data['macd_signal']
        
        # Calculate trend EMAs
        data['ema_short'] = data['close'].ewm(span=self.ema_short, adjust=False).mean()
        data['ema_long'] = data['close'].ewm(span=self.ema_long, adjust=False).mean()
        
        # Calculate EMA slope (rate of change) to assess trend strength
        data['ema_long_slope'] = data['ema_long'].diff(5)  # 5-period slope
        
        # Calculate histogram momentum (change in histogram)
        data['histogram_momentum'] = data['macd_histogram'].diff()
        
        # Trend direction indicator
        data['trend'] = np.where(data['ema_short'] > data['ema_long'], 1, -1)
        
        return data
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate trading signal based on MACD and EMA"""
        
        # Need enough data for indicators
        min_periods = max(self.macd_slow, self.ema_long) + self.macd_signal + 5
        if len(data) < min_periods:
            return 'HOLD'
        
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Check for NaN values
        required_indicators = ['macd_line', 'macd_signal', 'macd_histogram', 'ema_short', 'ema_long']
        if any(pd.isna(current[ind]) for ind in required_indicators):
            return 'HOLD'
        
        # Detect MACD crossovers
        bullish_crossover = (current['macd_line'] > current['macd_signal'] and 
                            previous['macd_line'] <= previous['macd_signal'])
        
        bearish_crossover = (current['macd_line'] < current['macd_signal'] and 
                            previous['macd_line'] >= previous['macd_signal'])
        
        # BUY Signal: Bullish MACD crossover in uptrend
        if bullish_crossover:
            # Trend filter: Price should be above long EMA
            if self.use_trend_filter and current['close'] < current['ema_long']:
                logger.debug("MACD bullish crossover but price below long EMA")
                return 'HOLD'
            
            # Additional confirmation: histogram should be growing
            if current['histogram_momentum'] > 0 or abs(current['macd_histogram']) > self.min_histogram_value:
                logger.info(f"BUY signal: MACD crossover, MACD={current['macd_line']:.4f}, "
                          f"Histogram={current['macd_histogram']:.4f}")
                return 'BUY'
        
        # SELL Signal: Bearish MACD crossover in downtrend
        elif bearish_crossover:
            # Trend filter: Price should be below long EMA
            if self.use_trend_filter and current['close'] > current['ema_long']:
                logger.debug("MACD bearish crossover but price above long EMA")
                return 'HOLD'
            
            # Additional confirmation: histogram should be declining
            if current['histogram_momentum'] < 0 or abs(current['macd_histogram']) > self.min_histogram_value:
                logger.info(f"SELL signal: MACD crossover, MACD={current['macd_line']:.4f}, "
                          f"Histogram={current['macd_histogram']:.4f}")
                return 'SELL'
        
        return 'HOLD'
    
    def should_enter(self, data: pd.DataFrame) -> bool:
        """Additional entry filters for trend following"""
        
        if not super().should_enter(data):
            return False
        
        current = data.iloc[-1]
        
        # Check trend strength - avoid weak trends
        if abs(current['ema_long_slope']) < 0.01:
            logger.debug("Trend too weak - skipping entry")
            return False
        
        # For additional safety, check if EMAs are aligned with the signal
        signal = self.generate_signal(data)
        if signal == 'BUY':
            # In uptrend, short EMA should be above long EMA
            if current['ema_short'] <= current['ema_long']:
                logger.debug("EMAs not aligned for bullish entry")
                return False
        elif signal == 'SELL':
            # In downtrend, short EMA should be below long EMA
            if current['ema_short'] >= current['ema_long']:
                logger.debug("EMAs not aligned for bearish entry")
                return False
        
        return True
    
    def should_exit(self, data: pd.DataFrame, current_price: float) -> bool:
        """Custom exit logic for trend following"""
        
        # Check default exit conditions (stop loss, take profit)
        if super().should_exit(data, current_price):
            return True
        
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Exit on opposite MACD crossover
        if self.position == 'LONG':
            # Exit long if MACD crosses below signal
            if (current['macd_line'] < current['macd_signal'] and 
                previous['macd_line'] >= previous['macd_signal']):
                logger.info("Exit LONG: MACD bearish crossover")
                return True
            
            # Exit if price falls below long EMA (trend reversal)
            if current['close'] < current['ema_long']:
                logger.info("Exit LONG: Price below long EMA")
                return True
        
        elif self.position == 'SHORT':
            # Exit short if MACD crosses above signal
            if (current['macd_line'] > current['macd_signal'] and 
                previous['macd_line'] <= previous['macd_signal']):
                logger.info("Exit SHORT: MACD bullish crossover")
                return True
            
            # Exit if price rises above long EMA (trend reversal)
            if current['close'] > current['ema_long']:
                logger.info("Exit SHORT: Price above long EMA")
                return True
        
        return False


# Configuration example for this strategy
EXAMPLE_CONFIG = {
    "enabled": True,
    "description": "MACD + EMA trend following strategy",
    "parameters": {
        "symbol": "BTC/USDT",
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "ema_short": 20,
        "ema_long": 50,
        "use_trend_filter": True,
        "min_histogram_value": 0.0
    },
    "risk_settings": {
        "position_size": 100,
        "stop_loss_pct": 2.5,
        "take_profit_pct": 6.0
    }
}


if __name__ == '__main__':
    """Test the strategy with sample data"""
    print("Testing MACD + EMA Trend Following Strategy")
    print("=" * 60)
    
    # Generate sample data with trending behavior
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=300, freq='1h')
    
    # Generate trending price data
    trend = np.linspace(0, 20, 300)  # Upward trend
    noise = np.random.randn(300) * 2
    prices = 100 + trend + noise
    
    sample_data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(300) * 0.001),
        'high': prices * (1 + abs(np.random.randn(300)) * 0.005),
        'low': prices * (1 - abs(np.random.randn(300)) * 0.005),
        'close': prices,
        'volume': np.random.randint(1000, 10000, 300)
    }, index=dates)
    
    # Initialize strategy
    strategy = MACDEMATrend(EXAMPLE_CONFIG)
    
    # Calculate indicators
    sample_data = strategy.calculate_indicators(sample_data)
    
    # Test signal generation
    signals = []
    for i in range(60, len(sample_data)):
        current_data = sample_data.iloc[:i+1]
        signal = strategy.generate_signal(current_data)
        
        if signal != 'HOLD':
            current = current_data.iloc[-1]
            signals.append({
                'timestamp': current_data.index[-1],
                'signal': signal,
                'price': current['close'],
                'macd_line': current['macd_line'],
                'macd_signal': current['macd_signal'],
                'trend': 'UP' if current['ema_short'] > current['ema_long'] else 'DOWN'
            })
    
    # Print results
    print(f"\nGenerated {len(signals)} trading signals:\n")
    for sig in signals[:10]:  # Show first 10
        print(f"{sig['timestamp']}: {sig['signal']:4s} @ ${sig['price']:7.2f} | "
              f"MACD: {sig['macd_line']:6.3f} | Signal: {sig['macd_signal']:6.3f} | "
              f"Trend: {sig['trend']}")
    
    if len(signals) > 10:
        print(f"\n... and {len(signals) - 10} more signals")
    
    print("\n" + "=" * 60)
    print("Strategy test complete!")
