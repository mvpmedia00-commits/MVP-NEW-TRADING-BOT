"""
Market Probability (MP) Extreme Range Strategy
Created for probabilistic MP-style execution
"""

import pandas as pd
from typing import Dict, Any
from datetime import time

from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MPExtremeRangeStrategy(BaseStrategy):
    """
    MP Strategy Logic:
    - Trade ONLY at range extremes
    - Avoid middle of the box
    - Directional pressure filter
    - Kill Zone execution
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.range_lookback = self.parameters.get('range_lookback', 50)
        self.ema_period = self.parameters.get('ema_period', 20)

        logger.info("MP Extreme Range Strategy initialized")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Range box
        df['range_high'] = df['high'].rolling(self.range_lookback).max()
        df['range_low'] = df['low'].rolling(self.range_lookback).min()
        df['range'] = df['range_high'] - df['range_low']

        # Position in range (0 = bottom, 1 = top)
        df['range_position'] = (df['close'] - df['range_low']) / df['range']

        # Directional pressure (MP-friendly)
        df['ema'] = df['close'].ewm(span=self.ema_period).mean()
        df['ema_slope'] = df['ema'] - df['ema'].shift(1)

        return df

    def in_kill_zone(self, timestamp) -> bool:
        """
        Kill Zone: 2 AM – 12 PM EST
        """
        est_time = timestamp.tz_convert('US/Eastern').time()
        return time(2, 0) <= est_time <= time(12, 0)

    def generate_signal(self, data: pd.DataFrame) -> str:
        df = self.calculate_indicators(data)

        if len(df) < self.range_lookback:
            return 'HOLD'

        latest = df.iloc[-1]

        # Time filter
        if not self.in_kill_zone(latest.name):
            return 'HOLD'

        range_pos = latest['range_position']
        ema_slope = latest['ema_slope']

        # =========================
        # MP BUY LOGIC (Bottom Edge)
        # =========================
        if range_pos <= 0.2 and ema_slope >= 0:
            logger.info("MP BUY: Bottom of range with upward pressure")
            return 'BUY'

        # =========================
        # MP SELL LOGIC (Top Edge)
        # =========================
        if range_pos >= 0.8 and ema_slope <= 0:
            logger.info("MP SELL: Top of range with downward pressure")
            return 'SELL'

        # =========================
        # MIDDLE = DANGER ZONE
        # =========================
        return 'HOLD'
