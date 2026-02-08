"""
LGM (Let's Go Money) strategy
Rule-only decision engine with no MP logic mixed in.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Any, Dict, Optional, Set
from zoneinfo import ZoneInfo

import pandas as pd

from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LgmTradeState:
    direction: str
    entry_price: float
    entry_index: int


class LGMStrategy(BaseStrategy):
    """
    LGM rule engine (pending-only entries, strict filters).

    Expects these optional columns if available:
    - arrow_color: str ("gold", "purple", "red", "green")
    - line_of_scrimmage: float
    - adr: float
    - daily_high: float
    - daily_low: float
    - x_signal: bool
    - candle_reversal_confirmed: bool
    - x_against_position: bool
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.symbol = self.parameters.get("symbol", "BTC/USDT")
        self.timezone = ZoneInfo(self.parameters.get("timezone", "US/Eastern"))
        self.killzone_start = self._parse_time(self.parameters.get("killzone_start", "02:00"))
        self.killzone_end = self._parse_time(self.parameters.get("killzone_end", "12:00"))
        self.allowed_days = self._parse_days(self.parameters.get("allowed_days", ["tuesday", "wednesday", "thursday"]))

        self.max_trades_per_day = int(self.parameters.get("max_trades_per_day", 3))
        self.max_trades_per_pair = int(self.parameters.get("max_trades_per_pair_per_day", 1))
        self.min_lot_size = float(self.risk_settings.get("position_size", self.parameters.get("min_lot_size", 10.0)))
        self.distance_from_line_pct = float(self.parameters.get("distance_from_line_pct", 0.35))
        self.adr_low_pct = float(self.parameters.get("adr_low_pct", 0.70))
        self.adr_high_pct = float(self.parameters.get("adr_high_pct", 0.85))
        self.checkpoints = self.parameters.get("checkpoints", [8, 16, 20])
        self.disable_after_losses = int(self.parameters.get("disable_after_losses", 2))

        self._missing_columns_logged: Set[str] = set()
        self._daily_reset_date: Optional[datetime.date] = None
        self._trades_today = 0
        self._pair_trades_today = 0
        self._losses_in_row = 0
        self._disabled_today = False
        self._active_trade: Optional[LgmTradeState] = None
        self._last_confidence: Optional[str] = None
        self._reduce_size_today = False

        logger.info(f"LGMStrategy initialized for {self.symbol}")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.copy()

    def generate_signal(self, data: pd.DataFrame) -> str:
        df = self.calculate_indicators(data)
        if df.empty:
            return "HOLD"

        timestamp = self._get_latest_timestamp(df)
        if not timestamp:
            return "HOLD"

        self._reset_daily_counters(timestamp)

        if self._disabled_today:
            return "HOLD"

        if not self._in_killzone(timestamp):
            return "HOLD"

        self._reduce_size_today = not self._allowed_day(timestamp)

        if self._trades_today >= self.max_trades_per_day:
            return "HOLD"

        if self._pair_trades_today >= self.max_trades_per_pair:
            return "HOLD"

        arrow = self._get_required_column(df, "arrow_color")
        if arrow is None:
            return "HOLD"

        arrow = str(arrow).lower()
        if arrow in {"red", "green"}:
            return "HOLD"
        if arrow not in {"gold", "purple"}:
            return "HOLD"

        current_price = float(df["close"].iloc[-1])
        adr = self._get_required_column(df, "adr")
        line_of_scrimmage = self._get_required_column(df, "line_of_scrimmage")
        daily_high = self._get_required_column(df, "daily_high")
        daily_low = self._get_required_column(df, "daily_low")

        if adr is None or line_of_scrimmage is None or daily_high is None or daily_low is None:
            return "HOLD"

        if adr <= 0:
            return "HOLD"

        distance = abs(current_price - float(line_of_scrimmage))
        if distance < self.distance_from_line_pct * float(adr):
            return "HOLD"

        confidence = self._adr_confidence(current_price, float(daily_high), float(daily_low), float(adr))
        if confidence is None:
            return "HOLD"

        self._last_confidence = confidence

        if self._active_trade:
            return "HOLD"

        self._active_trade = LgmTradeState(direction="BUY", entry_price=current_price, entry_index=len(df) - 1)
        self._trades_today += 1
        self._pair_trades_today += 1
        logger.info(f"{self.symbol} LGM pending entry allowed ({arrow})")
        return "BUY"

    def manage_trade(self, data: pd.DataFrame) -> str:
        if not self._active_trade:
            return "HOLD"

        df = data
        if df.empty:
            return "HOLD"

        current_price = float(df["close"].iloc[-1])
        candles_in_trade = (len(df) - 1) - self._active_trade.entry_index

        if candles_in_trade >= int(self.checkpoints[0]):
            if not self._in_profit(current_price):
                self._reset_trade()
                return "EXIT"

        x_signal = self._get_optional_column(df, "x_signal")
        x_against = self._get_optional_column(df, "x_against_position")
        candle_confirm = self._get_optional_column(df, "candle_reversal_confirmed")

        if x_signal and candle_confirm:
            self._reset_trade()
            return "EXIT"

        if x_signal and x_against and self._in_profit(current_price):
            self._reset_trade()
            return "EXIT"

        return "HOLD"

    def get_position_size(self) -> float:
        position_size = self.min_lot_size
        if self._last_confidence == "low":
            position_size = self.min_lot_size
        if self._reduce_size_today:
            position_size = position_size * 0.5
        return max(position_size, 0.0)

    def record_trade_result(self, pnl: float):
        if pnl < 0:
            self._losses_in_row += 1
            if self._losses_in_row >= self.disable_after_losses:
                self._disabled_today = True
        else:
            self._losses_in_row = 0

    def _reset_trade(self):
        self._active_trade = None
        self._last_confidence = None

    def _in_profit(self, current_price: float) -> bool:
        if not self._active_trade:
            return False
        if self._active_trade.direction == "BUY":
            return current_price > self._active_trade.entry_price
        return current_price < self._active_trade.entry_price

    def _reset_daily_counters(self, now: datetime):
        current_date = now.date()
        if self._daily_reset_date != current_date:
            self._daily_reset_date = current_date
            self._trades_today = 0
            self._pair_trades_today = 0
            self._losses_in_row = 0
            self._disabled_today = False

    def _adr_confidence(self, price: float, daily_high: float, daily_low: float, adr: float) -> Optional[str]:
        adr_used = max(abs(price - daily_low), abs(daily_high - price))
        usage_pct = adr_used / adr if adr else 0
        if usage_pct >= self.adr_high_pct:
            return "high"
        if usage_pct >= self.adr_low_pct:
            return "low"
        return "low"

    def _parse_time(self, value: str) -> time:
        hour, minute = value.split(":")
        return time(int(hour), int(minute))

    def _parse_days(self, values) -> Set[int]:
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        parsed = set()
        for value in values:
            if isinstance(value, int):
                parsed.add(value)
            else:
                parsed.add(day_map.get(str(value).lower(), 0))
        return parsed

    def _in_killzone(self, now: datetime) -> bool:
        est_time = now.astimezone(self.timezone).time()
        return self.killzone_start <= est_time <= self.killzone_end

    def _allowed_day(self, now: datetime) -> bool:
        return now.astimezone(self.timezone).weekday() in self.allowed_days

    def _get_latest_timestamp(self, df: pd.DataFrame) -> Optional[datetime]:
        if "timestamp" not in df.columns:
            self._log_missing("timestamp")
            return None

        ts = df["timestamp"].iloc[-1]
        try:
            if isinstance(ts, (int, float)):
                unit = "ms" if ts > 1_000_000_000_000 else "s"
                return pd.to_datetime(ts, unit=unit, utc=True).to_pydatetime()
            if isinstance(ts, pd.Timestamp):
                if ts.tzinfo is None:
                    return ts.tz_localize("UTC").to_pydatetime()
                return ts.to_pydatetime()
            return pd.to_datetime(ts, utc=True).to_pydatetime()
        except Exception:
            self._log_missing("timestamp")
            return None

    def _get_required_column(self, df: pd.DataFrame, column: str):
        if column not in df.columns:
            self._log_missing(column)
            return None
        return df[column].iloc[-1]

    def _get_optional_column(self, df: pd.DataFrame, column: str):
        if column not in df.columns:
            return None
        return df[column].iloc[-1]

    def _log_missing(self, column: str):
        if column not in self._missing_columns_logged:
            logger.warning(f"LGM missing column: {column}")
            self._missing_columns_logged.add(column)
