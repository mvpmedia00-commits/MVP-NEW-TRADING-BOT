"""
Market Probability Crypto Strategy
Tuned for BTC, ETH, XRP, DOGE, SHIB, TRUMP (24/7 crypto markets)

Strategy adapts MP logic for:
- Crypto liquidity windows (Asia + London-NY overlap)
- Meme coin protection (DOGE, SHIB, TRUMP)
- Explosive volatility and fake breakouts
- No kill zone time filter (crypto is 24/7)

Created by Coach Zuri Aki - MP Framework
Crypto adaptation for Crypto.com exchange
"""

import pandas as pd
from typing import Dict, Any
from datetime import time

from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MPCryptoStrategy(BaseStrategy):
    """
    Market Probability Crypto Strategy
    Tuned for BTC, ETH, XRP, DOGE, SHIB, TRUMP
    
    Core Mechanics:
    - Liquidity window filtering (Asia 00:00-04:00 UTC + London-NY 12:00-16:00 UTC)
    - Range-based entries at extremes (20% for majors, 15% for memes)
    - EMA slope directional confirmation
    - Meme coin hard mode: BUY ONLY, no shorts, tighter entries
    - Volatility exhaustion exits
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.symbol = config.get("symbol", "BTC")
        self.session_lookback = self.parameters.get("session_lookback", 96)  # ~4 hours of 15min candles
        self.ema_period = self.parameters.get("ema_period", 20)
        self.cooldown_candles = self.parameters.get("cooldown_candles", 8)
        self.volatility_threshold = self.parameters.get("volatility_threshold", 0.10)

        # Trade state management
        self.trade_open = False
        self.trade_direction = None
        self.entry_index = None
        self.cooldown = 0

        logger.info(f"MPCryptoStrategy initialized for {self.symbol}")

    # -------- CRYPTO LIQUIDITY WINDOWS -------- #

    def in_liquidity_window(self, timestamp) -> bool:
        """
        Crypto has liquid hours:
        - 00:00 – 04:00 UTC (Asia liquidity)
        - 12:00 – 16:00 UTC (London → NY overlap)
        
        Avoid: 20:00–23:59 UTC (thin moves, fakes)
        Weekends: Optional filter (crypto still trades but thinner)
        """
        try:
            utc = timestamp.tz_convert("UTC").time() if hasattr(timestamp, 'tz_convert') else timestamp.time()
        except:
            # Fallback if timezone aware conversion fails
            return True

        asia = time(0, 0) <= utc <= time(4, 0)
        london_ny = time(12, 0) <= utc <= time(16, 0)

        return asia or london_ny

    # -------- INDICATORS -------- #

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate range, position, and directional bias
        
        Range: High/low over session_lookback candles
        Position: Where price sits in range (0.0 = bottom, 1.0 = top)
        EMA Slope: Directional bias (momentum)
        Volatility: Range as percent of close (exhaustion detector)
        """
        df = data.copy()

        # Range extremes
        df["high_range"] = df["high"].rolling(self.session_lookback).max()
        df["low_range"] = df["low"].rolling(self.session_lookback).min()
        df["range"] = df["high_range"] - df["low_range"]

        # Where are we in the range? (0.0 = bottom, 1.0 = top)
        df["range_position"] = (df["close"] - df["low_range"]) / (df["range"] + 1e-8)
        df["range_position"] = df["range_position"].clip(0, 1)

        # Directional bias
        df["ema"] = df["close"].ewm(span=self.ema_period).mean()
        df["ema_slope"] = df["ema"].diff()

        # Volatility (range as % of close) - exhaustion detection
        df["volatility"] = df["range"] / (df["close"] + 1e-8)

        return df

    # -------- SIGNAL GENERATION -------- #

    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        MP Crypto Entry Logic
        
        Filters:
        1. Liquidity window (UTC times)
        2. Range position (avoid middle)
        3. Directional bias (EMA slope)
        4. Meme restrictions (DOGE/SHIB/TRUMP: BUY ONLY)
        
        Entry Rules:
        - BUY: Bottom 15-20% + upward EMA slope
        - SELL: Top 85%+ + downward EMA slope (majors only)
        """
        df = self.calculate_indicators(data)

        if len(df) < self.session_lookback:
            return "HOLD"

        latest = df.iloc[-1]

        # -------- COOLDOWN FILTER (prevent overtrading) -------- #
        if self.cooldown > 0:
            self.cooldown -= 1
            return "HOLD"

        # -------- LIQUIDITY WINDOW FILTER -------- #
        if not self.in_liquidity_window(latest.name):
            return "HOLD"

        # -------- MIDDLE OF RANGE FILTER (avoid chop) -------- #
        # Only trade extremes: avoid if 30-70% of range
        if 0.30 < latest["range_position"] < 0.70:
            return "HOLD"

        # -------- DIRECTIONAL BIAS -------- #
        bullish = latest["ema_slope"] > 0
        bearish = latest["ema_slope"] < 0

        # -------- MEME COIN DETECTION -------- #
        meme = self.symbol in ["DOGE", "SHIB", "TRUMP"]

        # -------- BUY SIGNAL (all pairs) -------- #
        # Entry zone: 15% for memes, 20% for majors
        entry_zone = 0.15 if meme else 0.20

        if (
            not self.trade_open
            and latest["range_position"] <= entry_zone
            and bullish
        ):
            self.trade_open = True
            self.trade_direction = "BUY"
            self.entry_index = len(df) - 1
            logger.info(f"{self.symbol} BUY signal | Position: {latest['range_position']:.2%}")
            return "BUY"

        # -------- SELL SIGNAL (majors only) -------- #
        # MEME RESTRICTION: No sells for DOGE/SHIB/TRUMP
        if (
            not meme
            and not self.trade_open
            and latest["range_position"] >= 0.85
            and bearish
        ):
            self.trade_open = True
            self.trade_direction = "SELL"
            self.entry_index = len(df) - 1
            logger.info(f"{self.symbol} SELL signal | Position: {latest['range_position']:.2%}")
            return "SELL"

        return "HOLD"

    # -------- TRADE MANAGEMENT -------- #

    def manage_trade(self, data: pd.DataFrame) -> str:
        """
        Exit Logic:
        1. MP Checkpoint: Exit if price reverts to entry (micro loss)
        2. Volatility Exhaustion: Exit if volatility spikes (>10%) - momentum exhausted
        
        Goal: Scale out early, limit exposure to chop/reversals
        """
        if not self.trade_open:
            return "HOLD"

        df = data
        current_index = len(df) - 1
        candles_in_trade = current_index - self.entry_index

        # -------- MP CHECKPOINT (micro loss exit) -------- #
        # If 6+ candles and price back at entry → exit
        if candles_in_trade >= 6:
            entry_price = df["close"].iloc[self.entry_index]
            current_price = df["close"].iloc[-1]

            # BUY: Exit if price drops back to entry
            if self.trade_direction == "BUY" and current_price <= entry_price:
                logger.info(f"{self.symbol} EXIT (BUY revert) | Entry: {entry_price:.2f} | Current: {current_price:.2f}")
                self._reset_trade()
                return "EXIT"

            # SELL: Exit if price rises back to entry
            if self.trade_direction == "SELL" and current_price >= entry_price:
                logger.info(f"{self.symbol} EXIT (SELL revert) | Entry: {entry_price:.2f} | Current: {current_price:.2f}")
                self._reset_trade()
                return "EXIT"

        # -------- VOLATILITY EXHAUSTION EXIT -------- #
        # Crypto explosive moves → exit on volatility spike
        volatility_calc = self.calculate_indicators(df)
        if volatility_calc["volatility"].iloc[-1] > self.volatility_threshold:
            logger.info(f"{self.symbol} EXIT (volatility exhaustion) | Vol: {volatility_calc['volatility'].iloc[-1]:.2%}")
            self._reset_trade()
            return "EXIT"

        return "HOLD"

    # -------- TRADE STATE MANAGEMENT -------- #

    def _reset_trade(self):
        """Reset trade state and enter cooldown"""
        self.trade_open = False
        self.trade_direction = None
        self.entry_index = None
        self.cooldown = self.cooldown_candles


# -------- MEME COIN RESTRICTIONS -------- #

MEME_SYMBOLS = {"DOGE", "SHIB", "TRUMP"}

def is_meme_coin(symbol: str) -> bool:
    """Check if symbol is a meme coin (special handling required)"""
    base = symbol.split("_")[0] if "_" in symbol else symbol
    return base in MEME_SYMBOLS


__all__ = ["MPCryptoStrategy", "MEME_SYMBOLS", "is_meme_coin"]
