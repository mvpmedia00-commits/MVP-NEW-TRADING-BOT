"""
CSV trade logger
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Dict, Any


class TradeLogger:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_dir()
        self._ensure_header()

    def _ensure_dir(self):
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _ensure_header(self):
        if os.path.exists(self.file_path):
            return
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "event",
                "symbol",
                "side",
                "entry_price",
                "exit_price",
                "quantity",
                "pnl",
                "pnl_pct",
                "broker",
                "reason",
            ])

    def log(self, event: str, data: Dict[str, Any]):
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "symbol": data.get("symbol", ""),
            "side": data.get("side", ""),
            "entry_price": data.get("entry_price", ""),
            "exit_price": data.get("exit_price", ""),
            "quantity": data.get("quantity", ""),
            "pnl": data.get("pnl", ""),
            "pnl_pct": data.get("pnl_pct", ""),
            "broker": data.get("broker", ""),
            "reason": data.get("reason", ""),
        }
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                row["timestamp"],
                row["event"],
                row["symbol"],
                row["side"],
                row["entry_price"],
                row["exit_price"],
                row["quantity"],
                row["pnl"],
                row["pnl_pct"],
                row["broker"],
                row["reason"],
            ])
