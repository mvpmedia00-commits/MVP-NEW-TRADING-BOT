"""
Execution Guardrails Manager V2 - Enforces all pre-execution and execution safety checks
Integrates with OrderManager, Broker, and RiskEngine
"""

from typing import Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import threading
import time

from ..utils.logger import get_logger
from ..utils.execution_guardrails import (
    execute_trade,
    symbol_allowed,
    spread_ok,
    order_size_ok,
    meme_restrictions,
    MAX_SPREAD,
    MEME_COINS,
)

logger = get_logger(__name__)


class ExecutionGuardrailsManagerV2:
    """
    Enhanced execution layer with:
    1. Pre-execution validation (guardrails layer)
    2. Order lifecycle tracking
    3. Fill confirmation
    4. Execution logging & audit
    5. Retry logic with safety bounds
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize execution guardrails manager"""
        self._lock = threading.RLock()
        
        self.config = config or {}
        
        # Execution parameters
        self.fill_timeout = self.config.get('fill_timeout', 5)  # seconds
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1)  # seconds
        
        # Tracking
        self._order_history: list = []
        self._rejected_orders: Dict[str, list] = {}
        self._partial_fills: list = []
        
        logger.info(
            f"ExecutionGuardrailsManagerV2 initialized | "
            f"Fill timeout: {self.fill_timeout}s | Max retries: {self.max_retries}"
        )
    
    def validate_and_execute(
        self,
        broker,
        symbol: str,
        side: str,
        qty: float,
        bid: float,
        ask: float,
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Master execution function - runs all guardrails then executes order
        
        Args:
            broker: Broker instance with place_limit_order, get_order, cancel_order methods
            symbol: Trading pair (e.g., "BTC_USD")
            side: "BUY" or "SELL"
            qty: Order quantity
            bid: Current bid price
            ask: Current ask price
        
        Returns:
            (success: bool, error_message: str | None, order_result: dict | None)
        """
        with self._lock:
            try:
                # GUARD 1: Symbol whitelist
                if not symbol_allowed(symbol):
                    reason = f"Symbol {symbol} not in whitelist"
                    self._log_rejection(symbol, side, qty, reason)
                    logger.warning(f"❌ {reason}")
                    return False, reason, None
                
                # GUARD 2: Spread validation
                if not spread_ok(symbol, bid, ask):
                    spread_pct = ((ask - bid) / ask * 100)
                    reason = f"Spread {spread_pct:.3f}% exceeds limit"
                    self._log_rejection(symbol, side, qty, reason)
                    logger.warning(f"❌ {symbol} {reason}")
                    return False, reason, None
                
                # GUARD 3: Meme restrictions
                if not meme_restrictions(symbol, side):
                    reason = f"Meme coin {symbol}: {side} orders not allowed (BUY only)"
                    self._log_rejection(symbol, side, qty, reason)
                    logger.warning(f"❌ {reason}")
                    return False, reason, None
                
                # GUARD 4: Order size (minimum notional)
                from ..utils.execution_guardrails import build_limit_price
                limit_price = build_limit_price(side, bid, ask)
                
                if not order_size_ok(symbol, qty, limit_price):
                    reason = f"Order too small: ${qty * limit_price:.2f} < $10 minimum"
                    self._log_rejection(symbol, side, qty, reason)
                    logger.warning(f"❌ {reason}")
                    return False, reason, None
                
                # All guardrails passed → execute_trade()
                success, message = execute_trade(broker, symbol, side, qty, bid, ask)
                
                if success:
                    order_result = {
                        "symbol": symbol,
                        "side": side,
                        "qty": qty,
                        "price": limit_price,
                        "status": "FILLED",
                        "executed_at": datetime.utcnow().isoformat(),
                        "message": message,
                    }
                    
                    self._order_history.append(order_result)
                    logger.info(f"✅ Order executed: {message}")
                    
                    return True, None, order_result
                else:
                    # Order rejected or cancelled at execution layer
                    self._log_rejection(symbol, side, qty, message)
                    logger.warning(f"❌ Execution failed: {message}")
                    
                    return False, message, None
                    
            except Exception as e:
                error = f"Execution error: {str(e)}"
                logger.error(error, exc_info=True)
                self._log_rejection(symbol, side, qty, error)
                return False, error, None
    
    def _log_rejection(self, symbol: str, side: str, qty: float, reason: str):
        """Log rejected order"""
        rejection = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self._rejected_orders.setdefault(symbol, []).append(rejection)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        with self._lock:
            total_executed = len(self._order_history)
            total_rejected = sum(len(v) for v in self._rejected_orders.values())
            
            if total_executed == 0 and total_rejected == 0:
                return {
                    "total_executed": 0,
                    "total_rejected": 0,
                    "rejection_reasons": {},
                }
            
            # Count rejection reasons
            rejection_reasons: Dict[str, int] = {}
            for rejections in self._rejected_orders.values():
                for rej in rejections:
                    reason = rej['reason']
                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            
            return {
                "total_executed": total_executed,
                "total_rejected": total_rejected,
                "rejection_rate": (total_rejected / (total_executed + total_rejected) * 100) 
                                  if (total_executed + total_rejected) > 0 else 0,
                "rejection_reasons": rejection_reasons,
                "by_symbol": {
                    symbol: len(rejections) 
                    for symbol, rejections in self._rejected_orders.items()
                },
            }
    
    def audit_log(self) -> list:
        """Get complete audit trail"""
        with self._lock:
            return self._order_history + [
                {**rej, "status": "REJECTED"}
                for rejections in self._rejected_orders.values()
                for rej in rejections
            ]


__all__ = ["ExecutionGuardrailsManagerV2"]
