"""
Range & Exhaustion Engine - Calculates rolling ranges and volatility
Implements chop filters, range expansion detection, and exhaustion signals
"""

from typing import Dict, Optional, Any, Tuple
import pandas as pd
import numpy as np
import threading

from ..utils.logger import get_logger

logger = get_logger(__name__)


class RangeAnalyzer:
    """
    Analyzes market range and volatility for VG trading
    
    Tracks:
    - Rolling session high/low
    - Range position (where price sits in range)
    - Range expansion/contraction
    - Volatility (ADR%)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize range analyzer"""
        self._lock = threading.RLock()
        
        self.config = config or {}
        
        # Range parameters
        self.session_lookback = self.config.get('session_lookback', 96)  # ~4 hours
        self.min_range = self.config.get('min_range_pct', 0.5)  # Minimum 0.5% range
        self.chop_threshold = self.config.get('chop_threshold_pct', 1.0)  # < 1% = chop
        self.exhaustion_threshold = self.config.get('exhaustion_threshold_pct', 10.0)  # > 10% = exhaustion
        
        # Cache per symbol
        self._range_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(
            f"RangeAnalyzer initialized | Lookback: {self.session_lookback} candles | "
            f"Min range: {self.min_range}% | Chop < {self.chop_threshold}% | "
            f"Exhaustion > {self.exhaustion_threshold}%"
        )
    
    def analyze(
        self,
        symbol: str,
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Comprehensive range analysis
        
        Args:
            symbol: Trading symbol
            data: DataFrame with OHLCV data
        
        Returns:
            Analysis dict with:
            - range_high, range_low, range_size
            - range_position (0.0 to 1.0)
            - volatility_pct
            - is_chop, is_exhaustion
            - expansion_level
        """
        with self._lock:
            if len(data) < self.session_lookback:
                logger.warning(f"{symbol}: Insufficient data ({len(data)} < {self.session_lookback})")
                return self._empty_analysis()
            
            try:
                df = data.copy()
                
                # Calculate rolling highs/lows
                df['range_high'] = df['high'].rolling(self.session_lookback).max()
                df['range_low'] = df['low'].rolling(self.session_lookback).min()
                df['range_size'] = df['range_high'] - df['range_low']
                
                # Get latest values
                latest = df.iloc[-1]
                range_high = latest['range_high']
                range_low = latest['range_low']
                range_size = latest['range_size']
                close_price = latest['close']
                
                # Calculate range position (0.0 = bottom, 1.0 = top)
                if range_size > 0:
                    range_position = (close_price - range_low) / range_size
                    range_position = np.clip(range_position, 0.0, 1.0)
                else:
                    range_position = 0.5
                
                # Calculate volatility as % of close
                volatility_pct = (range_size / close_price * 100) if close_price > 0 else 0
                
                # Determine conditions
                is_chop = volatility_pct < self.chop_threshold
                is_exhaustion = volatility_pct > self.exhaustion_threshold
                
                # Range expansion level (0.0 = contraction, 1.0+ = expansion)
                avg_range = df['range_size'].rolling(self.session_lookback).mean().iloc[-2] if len(df) > 1 else range_size
                if avg_range > 0:
                    expansion_level = range_size / avg_range
                else:
                    expansion_level = 1.0
                
                # Determine zone
                if range_position <= 0.2:
                    zone = "BOTTOM"
                elif range_position <= 0.35:
                    zone = "LOWER RANGE"
                elif range_position <= 0.65:
                    zone = "MIDDLE"
                elif range_position <= 0.8:
                    zone = "UPPER RANGE"
                else:
                    zone = "TOP"
                
                analysis = {
                    "symbol": symbol,
                    "timestamp": latest.get('timestamp', pd.Timestamp.utcnow()),
                    "price": close_price,
                    "range_high": range_high,
                    "range_low": range_low,
                    "range_size": range_size,
                    "range_position": float(range_position),
                    "zone": zone,
                    "volatility_pct": volatility_pct,
                    "is_chop": is_chop,
                    "is_exhaustion": is_exhaustion,
                    "expansion_level": expansion_level,
                    "min_range_met": volatility_pct >= self.min_range,
                }
                
                self._range_cache[symbol] = analysis
                
                logger.debug(
                    f"{symbol} Range: ${range_low:.2f}-${range_high:.2f} | "
                    f"Position: {range_position:.1%} ({zone}) | "
                    f"Vol: {volatility_pct:.2f}%"
                )
                
                return analysis
                
            except Exception as e:
                logger.error(f"Error analyzing range for {symbol}: {e}", exc_info=True)
                return self._empty_analysis()
    
    def can_trade(self, analysis: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Determine if current market conditions allow trading
        
        Returns:
            (can_trade: bool, reason: str | None)
        """
        # Chop filter
        if analysis.get('is_chop'):
            return False, f"Market chop ({analysis.get('volatility_pct', 0):.2f}%)"
        
        # Range expansion check
        if not analysis.get('min_range_met'):
            return False, f"Range too small ({analysis.get('volatility_pct', 0):.2f}% < {self.min_range}%)"
        
        return True, None
    
    def should_exit_on_exhaustion(self, analysis: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check if volatility exhaustion suggests exit
        
        Exhaustion = explosion of range → move losing energy
        """
        if analysis.get('is_exhaustion'):
            return True, f"Volatility exhaustion ({analysis.get('volatility_pct', 0):.2f}% > {self.exhaustion_threshold}%)"
        
        return False, None
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis dict"""
        return {
            "symbol": "N/A",
            "price": 0.0,
            "range_high": 0.0,
            "range_low": 0.0,
            "range_size": 0.0,
            "range_position": 0.5,
            "zone": "UNKNOWN",
            "volatility_pct": 0.0,
            "is_chop": False,
            "is_exhaustion": False,
            "expansion_level": 1.0,
            "min_range_met": False,
        }
    
    def get_cache(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis for symbol"""
        with self._lock:
            return self._range_cache.get(symbol)
    
    def chart_data(self) -> Dict[str, Any]:
        """Get data suitable for dashboard charting"""
        with self._lock:
            return {
                "updated_at": pd.Timestamp.utcnow().isoformat(),
                "analyses": self._range_cache.copy(),
            }


class ZoneClassifier:
    """Classifies range zones for entry/exit decisions"""
    
    @staticmethod
    def get_zone(range_position: float) -> str:
        """Classify zone based on range position"""
        if range_position <= 0.15:
            return "ENTRY_BOTTOM"
        elif range_position <= 0.20:
            return "BOTTOM_EDGE"
        elif range_position <= 0.30:
            return "LOWER_RANGE"
        elif range_position < 0.70:
            return "MIDDLE_CHOP"
        elif range_position <= 0.80:
            return "UPPER_RANGE"
        elif range_position <= 0.85:
            return "TOP_EDGE"
        else:
            return "ENTRY_TOP"
    
    @staticmethod
    def is_entry_zone(range_position: float, direction: str, is_meme: bool = False) -> bool:
        """
        Check if range position is in valid entry zone
        
        direction: "BUY" or "SELL"
        is_meme: If True, use tighter thresholds
        """
        if direction == "BUY":
            # BUY: Bottom 20% for majors, 15% for memes
            threshold = 0.15 if is_meme else 0.20
            return range_position <= threshold
        
        elif direction == "SELL":
            # SELL: Top 15-20% (no sells for memes)
            return range_position >= 0.80
        
        return False
    
    @staticmethod
    def is_danger_zone(range_position: float) -> bool:
        """Check if in middle-of-range danger zone (30-70%)"""
        return 0.30 < range_position < 0.70


__all__ = ["RangeAnalyzer", "ZoneClassifier"]
