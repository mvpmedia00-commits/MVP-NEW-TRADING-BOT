"""
Trade State Manager - Tracks trade lifecycle and VG checkpoints
Implements trade state machine: ARMED → OPEN → CHECKPOINT_1 → CHECKPOINT_2 → EXIT
"""

from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime
import threading

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TradeState(Enum):
    """Trade lifecycle states"""
    NO_TRADE = "no_trade"           # No position
    ARMED = "armed"                 # Ready to enter (signal received, pre-checks passed)
    ENTRY_PENDING = "entry_pending" # Entry order placed
    OPEN = "open"                   # Position opened
    CHECKPOINT_1 = "checkpoint_1"   # +6 candles: VG revert check
    CHECKPOINT_2 = "checkpoint_2"   # +12 candles: Range exhaustion check
    EXITING = "exiting"             # Exit order placed
    EXIT_CONFIRMED = "exit_confirmed"  # Position fully closed


class TradeLifecycle:
    """Represents a single trade lifecycle"""
    
    def __init__(
        self,
        symbol: str,
        direction: str,  # "BUY" or "SELL"
        entry_price: float,
        position_size: float,
        entry_time: datetime,
        range_position: float = 0.0,
        volatility: float = 0.0
    ):
        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.position_size = position_size
        self.entry_time = entry_time
        self.entry_candle_index = 0  # Will be set when entry confirmed
        
        # Entry context
        self.range_position = range_position  # 0.0-1.0 where trade entered
        self.volatility = volatility
        
        # State tracking
        self.state = TradeState.ARMED
        self.state_changed_at = entry_time
        self.state_history = [
            {"state": TradeState.ARMED, "timestamp": entry_time, "note": "Initial entry signal"}
        ]
        
        # Exit tracking
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[datetime] = None
        self.exit_reason: Optional[str] = None
        self.pnl: float = 0.0
        self.pnl_pct: float = 0.0
        
        # VG Checkpoints
        self.checkpoint_1_passed = False
        self.checkpoint_1_reason: Optional[str] = None
        self.checkpoint_1_at_candle = None
        
        self.checkpoint_2_passed = False
        self.checkpoint_2_reason: Optional[str] = None
        self.checkpoint_2_at_candle = None
        
    def advance_state(self, new_state: TradeState, note: str = ""):
        """Advance trade to new state"""
        if self.state == new_state:
            return  # Already in this state
        
        logger.info(
            f"{self.symbol} trade state: {self.state.value} → {new_state.value} | {note}"
        )
        
        self.state = new_state
        self.state_changed_at = datetime.utcnow()
        self.state_history.append({
            "state": new_state,
            "timestamp": self.state_changed_at,
            "note": note
        })
    
    def mark_checkpoint_1(self, passed: bool, reason: str, at_candle: int):
        """Mark VG checkpoint 1 (6 candles: revert check)"""
        self.checkpoint_1_passed = passed
        self.checkpoint_1_reason = reason
        self.checkpoint_1_at_candle = at_candle
        
        status = "PASSED" if passed else "FAILED"
        logger.debug(f"{self.symbol} Checkpoint 1: {status} | {reason}")
    
    def mark_checkpoint_2(self, passed: bool, reason: str, at_candle: int):
        """Mark VG checkpoint 2 (12 candles: exhaustion check)"""
        self.checkpoint_2_passed = passed
        self.checkpoint_2_reason = reason
        self.checkpoint_2_at_candle = at_candle
        
        status = "PASSED" if passed else "FAILED"
        logger.debug(f"{self.symbol} Checkpoint 2: {status} | {reason}")
    
    def confirm_exit(self, exit_price: float, reason: str):
        """Confirm trade exit"""
        self.exit_price = exit_price
        self.exit_time = datetime.utcnow()
        self.exit_reason = reason
        
        # Calculate P&L
        if self.direction == "BUY":
            self.pnl = (exit_price - self.entry_price) * self.position_size
        else:  # SELL
            self.pnl = (self.entry_price - exit_price) * self.position_size
        
        self.pnl_pct = (self.pnl / (self.entry_price * self.position_size)) * 100
        
        self.advance_state(TradeState.EXIT_CONFIRMED, f"Exit: {reason}")


class TradeStateManager:
    """
    Manages trade state for each symbol
    Tracks:
    - Current trade state
    - Trade lifecycle
    - VG checkpoints
    - Cooldowns
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize trade state manager"""
        self._lock = threading.RLock()
        
        self.config = config or {}
        self.cooldown_candles = self.config.get('cooldown_candles', 8)
        self.checkpoint_1_candles = self.config.get('checkpoint_1_candles', 6)
        self.checkpoint_2_candles = self.config.get('checkpoint_2_candles', 12)
        
        # Per-symbol trade state
        self._trades: Dict[str, Optional[TradeLifecycle]] = {}
        self._cooldowns: Dict[str, int] = {}  # Candles remaining in cooldown
        self._trade_history: Dict[str, list] = {}  # Completed trades per symbol
        
        logger.info(
            f"TradeStateManager initialized | "
            f"Cooldown: {self.cooldown_candles} candles | "
            f"CP1: {self.checkpoint_1_candles} candles | "
            f"CP2: {self.checkpoint_2_candles} candles"
        )
    
    def can_enter_trade(self, symbol: str) -> tuple[bool, Optional[str]]:
        """Check if symbol is eligible for new trade entry"""
        with self._lock:
            # Check if already in trade
            if self._trades.get(symbol):
                return False, f"{symbol}: Trade already open"
            
            # Check cooldown
            cooldown = self._cooldowns.get(symbol, 0)
            if cooldown > 0:
                return False, f"{symbol}: In cooldown ({cooldown} candles remaining)"
            
            return True, None
    
    def open_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        position_size: float,
        range_position: float = 0.0,
        volatility: float = 0.0
    ) -> TradeLifecycle:
        """Open a new trade"""
        with self._lock:
            can_enter, reason = self.can_enter_trade(symbol)
            if not can_enter:
                raise ValueError(reason or f"Cannot enter trade for {symbol}")
            
            trade = TradeLifecycle(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                position_size=position_size,
                entry_time=datetime.utcnow(),
                range_position=range_position,
                volatility=volatility
            )
            
            self._trades[symbol] = trade
            self._trade_history.setdefault(symbol, [])
            
            logger.info(
                f"{symbol} Trade OPENED | {direction} {position_size} @ ${entry_price:.2f} | "
                f"Range: {range_position:.1%}"
            )
            
            return trade
    
    def advance_checkpoint(self, symbol: str, candles_open: int) -> Optional[str]:
        """
        Advance trade through VG checkpoints
        
        Returns:
            Exit reason if checkpoint failed, None if still open
        """
        with self._lock:
            trade = self._trades.get(symbol)
            if not trade or trade.state == TradeState.EXIT_CONFIRMED:
                return None
            
            # Check Checkpoint 1 (6 candles)
            if (
                candles_open >= self.checkpoint_1_candles
                and not trade.checkpoint_1_passed
            ):
                # Checkpoint 1: VG revert check
                # If price hasn't moved in direction, exit
                # Implementation will check in calling code
                logger.debug(f"{symbol} reached Checkpoint 1 ({self.checkpoint_1_candles} candles)")
                trade.advance_state(TradeState.CHECKPOINT_1, "Checkpoint 1: Revert check")
            
            # Check Checkpoint 2 (12 candles)
            if (
                candles_open >= self.checkpoint_2_candles
                and not trade.checkpoint_2_passed
            ):
                logger.debug(f"{symbol} reached Checkpoint 2 ({self.checkpoint_2_candles} candles)")
                trade.advance_state(TradeState.CHECKPOINT_2, "Checkpoint 2: Exhaustion check")
            
            return None
    
    def close_trade(
        self,
        symbol: str,
        exit_price: float,
        reason: str
    ) -> Optional[TradeLifecycle]:
        """Close an existing trade"""
        with self._lock:
            trade = self._trades.get(symbol)
            if not trade:
                logger.warning(f"{symbol}: No open trade to close")
                return None
            
            trade.confirm_exit(exit_price, reason)
            
            # Log trade result
            logger.info(
                f"{symbol} Trade CLOSED | {reason} | "
                f"Entry: ${trade.entry_price:.2f} | Exit: ${exit_price:.2f} | "
                f"PnL: ${trade.pnl:.2f} ({trade.pnl_pct:.2f}%)"
            )
            
            # Move to history
            self._trade_history[symbol].append(trade)
            
            # Start cooldown
            self._cooldowns[symbol] = self.cooldown_candles
            self._trades[symbol] = None
            
            return trade
    
    def decrement_cooldowns(self):
        """Called each candle to decrement all cooldowns"""
        with self._lock:
            for symbol in list(self._cooldowns.keys()):
                if self._cooldowns[symbol] > 0:
                    self._cooldowns[symbol] -= 1
    
    def get_current_trade(self, symbol: str) -> Optional[TradeLifecycle]:
        """Get current trade for symbol"""
        with self._lock:
            return self._trades.get(symbol)
    
    def get_trade_history(self, symbol: str = None) -> list:
        """Get completed trade history"""
        with self._lock:
            if symbol:
                return self._trade_history.get(symbol, [])
            else:
                # Return all trades across all symbols
                all_trades = []
                for trades in self._trade_history.values():
                    all_trades.extend(trades)
                return sorted(all_trades, key=lambda t: t.entry_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trade statistics"""
        with self._lock:
            all_trades = self.get_trade_history()
            
            if not all_trades:
                return {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "avg_pnl": 0.0,
                    "max_win": 0.0,
                    "max_loss": 0.0,
                }
            
            total = len(all_trades)
            wins = len([t for t in all_trades if t.pnl > 0])
            losses = len([t for t in all_trades if t.pnl < 0])
            total_pnl = sum(t.pnl for t in all_trades)
            
            return {
                "total_trades": total,
                "winning_trades": wins,
                "losing_trades": losses,
                "win_rate": (wins / total * 100) if total > 0 else 0.0,
                "total_pnl": total_pnl,
                "avg_pnl": total_pnl / total if total > 0 else 0.0,
                "max_win": max((t.pnl for t in all_trades if t.pnl > 0), default=0.0),
                "max_loss": min((t.pnl for t in all_trades if t.pnl < 0), default=0.0),
            }


__all__ = ["TradeState", "TradeLifecycle", "TradeStateManager"]
