"""
LGM Indicator Layer

Calculates indicators WITHOUT making trade decisions.
Pure signal calculation (what exists), separate from decision logic (what to do).
"""

from __future__ import annotations

from typing import Dict, Optional
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)

__all__ = ['LGMIndicatorEngine']


class LGMIndicatorEngine:
    """
    Calculates LGM-required indicators from raw OHLCV data.
    
    Outputs (added columns):
    - arrow_color: str ("red", "green", "gold", "purple")
    - line_of_scrimmage: float (5 PM EST daily open)
    - adr: float (Average Daily Range)
    - daily_high: float
    - daily_low: float
    - pb1_level: float (Yellow line - first pullback)
    - pb2_level: float (Light blue - second pullback)
    - x_signal: bool (X pattern detected)
    - candle_reversal_confirmed: bool
    - x_against_position: bool
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.timezone = ZoneInfo(self.config.get("timezone", "US/Eastern"))
        self.adr_lookback = int(self.config.get("adr_lookback", 14))
        self.ema_fast = int(self.config.get("ema_fast", 20))
        self.ema_slow = int(self.config.get("ema_slow", 50))
        logger.info("LGMIndicatorEngine initialized")

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich OHLCV DataFrame with LGM indicators.
        
        Args:
            df: DataFrame with columns [timestamp, open, high, low, close, volume]
            
        Returns:
            Enriched DataFrame with LGM columns added
        """
        if df.empty:
            return df

        enriched = df.copy()

        # Ensure timestamp is datetime
        if "timestamp" in enriched.columns:
            enriched["timestamp"] = pd.to_datetime(enriched["timestamp"], unit="ms", utc=True)

        # Calculate daily metrics
        enriched = self._calculate_daily_metrics(enriched)

        # Calculate EMAs for directional bias
        enriched = self._calculate_emas(enriched)

        # Calculate arrow color
        enriched = self._calculate_arrow_color(enriched)

        # Calculate pullback levels
        enriched = self._calculate_pullback_levels(enriched)

        # Detect X signals
        enriched = self._detect_x_signals(enriched)

        # Log latest values for debugging
        if len(enriched) > 0:
            latest = enriched.iloc[-1]
            logger.info(
                f"LGM Enrichment Complete - "
                f"Arrow: {latest.get('arrow_color', 'N/A')}, "
                f"ADR: {latest.get('adr', 0):.2f}, "
                f"X Signal: {latest.get('x_signal', False)}, "
                f"Range Position: {latest.get('range_position', 0):.2%}"
            )

        return enriched

    def _calculate_daily_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ADR, daily high/low, line of scrimmage."""
        df = df.copy()

        # Line of Scrimmage: 5 PM EST daily open
        if "timestamp" in df.columns:
            df["est_time"] = df["timestamp"].dt.tz_convert(self.timezone)
            df["trading_day"] = df["est_time"].apply(self._get_trading_day)
        else:
            logger.warning("No timestamp column for Line of Scrimmage calculation")
            df["line_of_scrimmage"] = df["open"].iloc[0] if len(df) > 0 else 0
            df["daily_high"] = df["high"]
            df["daily_low"] = df["low"]
            df["adr"] = (df["high"] - df["low"]).rolling(self.adr_lookback).mean()
            return df

        # Calculate daily high/low/scrimmage per trading day
        df["line_of_scrimmage"] = 0.0
        df["daily_high"] = df["high"].iloc[0] if len(df) > 0 else 0
        df["daily_low"] = df["low"].iloc[0] if len(df) > 0 else 0

        for day in df["trading_day"].unique():
            day_mask = df["trading_day"] == day
            if day_mask.any():
                day_data = df[day_mask]
                scrimmage_idx = day_data.index[0]
                df.loc[day_mask, "line_of_scrimmage"] = df.loc[scrimmage_idx, "open"]
                df.loc[day_mask, "daily_high"] = day_data["high"].max()
                df.loc[day_mask, "daily_low"] = day_data["low"].min()

        # Calculate ADR (Average Daily Range)
        df["daily_range"] = df["daily_high"] - df["daily_low"]
        df["adr"] = df["daily_range"].rolling(self.adr_lookback, min_periods=1).mean()

        return df

    def _calculate_emas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate fast/slow EMAs for directional bias."""
        df = df.copy()
        df["ema_fast"] = df["close"].ewm(span=self.ema_fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.ema_slow, adjust=False).mean()
        df["ema_slope"] = df["ema_fast"] - df["ema_slow"]
        return df

    def _calculate_arrow_color(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate arrow color based on range position and EMA momentum.
        
        GOLD: Bottom 25% + upward EMA → Entry allowed
        PURPLE: Top 75% + downward EMA → Entry allowed
        GREEN: Mid-range + upward EMA → Entry blocked
        RED: Mid-range + downward EMA → Entry blocked
        """
        df = df.copy()

        # Range position (0 = bottom, 1 = top)
        df["range_size"] = df["daily_high"] - df["daily_low"]
        df["range_position"] = (df["close"] - df["daily_low"]) / df["range_size"]
        df["range_position"] = df["range_position"].fillna(0.5)
        df["range_position"] = df["range_position"].clip(0, 1)

        # Directional bias (EMA slope)
        df["ema_slope_normalized"] = df["ema_slope"].fillna(0)

        # Calculate arrow color
        def get_arrow(row):
            pos = row["range_position"]
            slope = row["ema_slope_normalized"]

            # GOLD: Bottom 25% + upward
            if pos <= 0.25 and slope > 0:
                return "gold"
            # PURPLE: Top 75% + downward
            elif pos >= 0.75 and slope < 0:
                return "purple"
            # GREEN: Mid-range + upward
            elif 0.25 < pos < 0.75 and slope > 0:
                return "green"
            # RED: Mid-range + downward
            elif 0.25 < pos < 0.75 and slope < 0:
                return "red"
            else:
                # Default based on range position
                return "green" if slope > 0 else "red"

        df["arrow_color"] = df.apply(get_arrow, axis=1)
        return df

    def _calculate_pullback_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Fibonacci pullback levels (38.2%, 50%)."""
        df = df.copy()

        # Pullback levels from daily range
        df["pb1_level"] = df["daily_high"] - (df["daily_high"] - df["daily_low"]) * 0.382
        df["pb2_level"] = df["daily_high"] - (df["daily_high"] - df["daily_low"]) * 0.5

        return df

    def _detect_x_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect X signals (EMA crosses with volume confirmation).
        
        Requirements:
        - EMA cross (fast crosses slow)
        - >0.5% strength filter
        - 1.5x volume spike
        """
        df = df.copy()

        # Detect EMA crosses
        ema_diff = df["ema_fast"] - df["ema_slow"]
        ema_diff_prev = ema_diff.shift(1)

        # Cross detection (sign change)
        crosses = (ema_diff_prev * ema_diff < 0) & (ema_diff != 0)

        # Strength filter: cross must be >0.5% of price
        strength_filter = (ema_diff.abs() / df["close"]) > 0.005

        # Volume spike: current > 1.5x average
        avg_volume = df["volume"].rolling(20, min_periods=1).mean()
        volume_spike = df["volume"] > (avg_volume * 1.5)

        # X signal = cross + strength + volume
        df["x_signal"] = crosses & strength_filter & volume_spike

        # Candle confirmation: next candle confirms direction
        df["candle_reversal_confirmed"] = df["x_signal"].shift(-1).fillna(False)

        return df

    def get_latest_signals(self, df: pd.DataFrame) -> Dict:
        """Extract latest signal values for debugging."""
        if df.empty:
            return {}

        latest = df.iloc[-1]
        return {
            "arrow_color": latest.get("arrow_color", "N/A"),
            "adr": float(latest.get("adr", 0)),
            "line_of_scrimmage": float(latest.get("line_of_scrimmage", 0)),
            "x_signal": bool(latest.get("x_signal", False)),
            "range_position": float(latest.get("range_position", 0)),
            "pb1_level": float(latest.get("pb1_level", 0)),
            "pb2_level": float(latest.get("pb2_level", 0)),
        }

    def _get_trading_day(self, est_time):
        """Determine trading day (resets at 5 PM EST)."""
        from datetime import timedelta
        # Trading day starts at 5 PM EST previous calendar day
        if est_time.hour >= 17:
            return est_time.date()
        else:
            return est_time.date() - timedelta(days=1)
