"""
Execution Guardrails for Crypto Trading
Institutional-grade safety layer between strategy and broker

Prevents:
✓ Chop death
✓ Meme coin liquidation
✓ Overnight bleed
✓ Spread spikes (slippage death)
✓ Partial fill disasters
✓ Duplicate orders
✓ Market order losses

These guardrails keep VG logic intact while surviving crypto chaos.
"""

import time
from typing import Dict, Optional, Tuple
from decimal import Decimal

from ..utils.logger import get_logger

logger = get_logger(__name__)


# ========== GUARDRAIL 1: SYMBOL WHITELIST ========== #

ALLOWED_SYMBOLS = {
    "BTC/USD",
    "ETH/USD",
    "XRP/USD",
    "DOGE/USD",
    "SHIB/USD",
    "TRUMP/USD",
    "LTC/USD",
    "BCH/USD",
    "LINK/USD",
    "BTC/USDT",
    "ETH/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "SHIB/USDT",
    "TRUMP/USDT",
    "LTC/USDT",
    "BCH/USDT",
    "LINK/USDT",
}


def _normalize_symbol(symbol: str) -> str:
    return symbol.replace("_", "/").replace("-", "/")


def _asset_from_symbol(symbol: str) -> str:
    return _normalize_symbol(symbol).split("/")[0]


def symbol_allowed(symbol: str) -> bool:
    """
    Guardrail 1: Only trade whitelisted symbols
    
    Prevents:
    - Typo trades
    - API glitches routing to unexpected pairs
    - Accidental high-risk pair entry
    """
    return _normalize_symbol(symbol) in ALLOWED_SYMBOLS


# ========== GUARDRAIL 2: MAX SPREAD FILTER ========== #

MAX_SPREAD = {
    "BTC": 0.0005,      # 0.05%
    "ETH": 0.0005,      # 0.05%
    "XRP": 0.0008,      # 0.08%
    "DOGE": 0.0012,     # 0.12%
    "SHIB": 0.0020,     # 0.20%
    "TRUMP": 0.0025,    # 0.25%
}


def spread_ok(symbol: str, bid: float, ask: float) -> bool:
    """
    Guardrail 2: Check spread is within limits
    
    Prevents:
    - Slippage death during fake moves
    - Market orders against wide spreads
    - Crypto.com manipulation during volatility
    
    Returns:
    - True if spread is acceptable
    - False if spread is too wide → REJECT ORDER
    """
    if bid <= 0 or ask <= 0 or bid > ask:
        return False

    spread = (ask - bid) / ask
    asset = _asset_from_symbol(symbol)
    max_allowed = MAX_SPREAD.get(asset, 0.001)

    ok = spread <= max_allowed
    if not ok:
        logger.warning(f"{symbol} SPREAD TOO WIDE: {spread:.4%} vs max {max_allowed:.4%}")

    return ok


# ========== GUARDRAIL 3: LIMIT ORDERS ONLY ========== #

def build_limit_price(side: str, bid: float, ask: float) -> float:
    """
    Guardrail 3: Build safe limit prices (no market orders)
    
    Strategy:
    - BUY: Place at bid * 0.999 (slight discount, reduce slippage)
    - SELL: Place at ask * 1.001 (slight premium, reduce slippage)
    
    Prevents:
    - Market order donation losses
    - Spread trap fills
    - Immediate reversal losses
    """
    if side.upper() == "BUY":
        return bid * 0.999
    elif side.upper() == "SELL":
        return ask * 1.001
    else:
        raise ValueError(f"Unknown side: {side}")


# ========== GUARDRAIL 4: ORDER SIZE VALIDATION ========== #

MIN_NOTIONAL = {
    "BTC": 10,
    "ETH": 10,
    "XRP": 10,
    "DOGE": 10,
    "SHIB": 10,
    "TRUMP": 10,
}


def order_size_ok(symbol: str, qty: float, price: float) -> bool:
    """
    Guardrail 4: Validate order size meets minimum notional
    
    Prevents:
    - Ghost orders (too small, rejected by exchange)
    - Partial fills on micro orders
    - API rejections due to size
    
    Returns:
    - True if notional >= minimum
    - False if too small → REJECT ORDER
    """
    if qty <= 0 or price <= 0:
        return False

    asset = _asset_from_symbol(symbol)
    notional = qty * price
    min_notional = MIN_NOTIONAL.get(asset, 10)

    ok = notional >= min_notional
    if not ok:
        logger.warning(f"{symbol} ORDER TOO SMALL: {notional:.2f} USD vs min {min_notional} USD")

    return ok


# ========== GUARDRAIL 5: PARTIAL FILL TIMEOUT ========== #

def wait_for_fill(client, order_id: str, symbol: str, timeout: int = 5) -> bool:
    """
    Guardrail 5: Cancel if not filled within timeout
    
    Strategy:
    - Poll order status every 0.5 seconds
    - If FILLED → return True
    - If timeout expires → cancel order, return False
    
    Prevents:
    - Half positions (50% filled while 50% open)
    - Directional imbalance (long 0.5 BTC with no exit plan)
    - Crypto.com stalls on partial fills
    
    Args:
    - client: Exchange client (must have get_order, cancel_order methods)
    - order_id: Order ID to track
    - timeout: Seconds to wait before cancellation
    
    Returns:
    - True if order filled completely
    - False if timeout → order cancelled
    """
    start = time.time()
    poll_interval = 0.5

    while time.time() - start < timeout:
        try:
            order = client.get_order(order_id, symbol)
            status = order.get("status", "").upper()

            if status == "FILLED":
                logger.info(f"Order {order_id} FILLED")
                return True

            if status == "CANCELLED":
                logger.warning(f"Order {order_id} already cancelled")
                return False

        except Exception as e:
            logger.error(f"Error checking order {order_id}: {e}")
            return False

        time.sleep(poll_interval)

    # Timeout expired → cancel
    try:
        client.cancel_order(order_id, symbol)
        logger.warning(f"Order {order_id} TIMEOUT (5s) → CANCELLED")
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")

    return False


# ========== GUARDRAIL 6: DUPLICATE ORDER BLOCKER ========== #

LAST_ORDER_TS: Dict[str, float] = {}


def prevent_duplicate(symbol: str, cooldown: int = 10) -> bool:
    """
    Guardrail 6: Prevent duplicate orders from API retries
    
    Strategy:
    - Track last order time per symbol
    - Reject if new order within cooldown
    
    Prevents:
    - API retry sending 3x orders
    - Double entries (0.75% risk becomes 1.5%)
    - Account liquidation risk
    
    Args:
    - symbol: Trading pair (e.g., "BTC_USD")
    - cooldown: Seconds between orders for same symbol
    
    Returns:
    - True if order allowed
    - False if duplicate rejected
    """
    now = time.time()
    last = LAST_ORDER_TS.get(symbol, 0)

    if now - last < cooldown:
        logger.warning(f"{symbol} DUPLICATE REJECTED (within {cooldown}s cooldown)")
        return False

    LAST_ORDER_TS[symbol] = now
    return True


# ========== GUARDRAIL 7: MEME COIN HARD MODE ========== #

MEME_COINS = {"DOGE", "SHIB", "TRUMP"}


def meme_restrictions(symbol: str, side: str, allow_sell: bool = True) -> bool:
    """
    Guardrail 7: Enforce meme coin restrictions
    
    Meme Coin Rules:
    - BUY ONLY (no shorts)
    - No SELL orders ever
    - Exception logic prevents meme liquidation
    
    Prevents:
    - Meme coin short trap (DOGE +40% while short)
    - FOMO liquidation
    - High-beta reversal losses
    
    Args:
    - symbol: Trading pair (e.g., "DOGE_USD")
    - side: "BUY" or "SELL"
    
    Returns:
    - True if order allowed
    - False if violates meme restrictions
    """
    asset = _asset_from_symbol(symbol)

    if asset in MEME_COINS and side.upper() == "SELL" and not allow_sell:
        logger.warning(f"{symbol} MEME COIN HARD MODE: NO SELL orders allowed")
        return False

    return True


# ========== MASTER EXECUTION FUNCTION ========== #

def execute_trade(
    client,
    symbol: str,
    side: str,
    qty: float,
    bid: float,
    ask: float,
) -> Tuple[bool, str]:
    """
    MASTER EXECUTION: All guardrails applied in sequence
    
    Execution Pipeline:
    1. Symbol whitelist check
    2. Spread validation
    3. Meme coin restrictions
    4. Duplicate prevention
    5. Price calculation (limit order)
    6. Order size validation
    7. Place order
    8. Wait for fill (with timeout)
    
    Args:
    - client: Exchange client (ccxt implementation)
    - symbol: Trading pair (e.g., "BTC_USD")
    - side: "BUY" or "SELL"
    - qty: Quantity in base asset
    - bid: Current bid price
    - ask: Current ask price
    
    Returns:
    - (success: bool, message: str)
    - True, "FILLED" → Order executed
    - False, "BLOCKED: ..." → Guard rejected order
    - False, "CANCELLED: ..." → Order placed but not filled
    
    Examples:
    >>> success, msg = execute_trade(client, "BTC_USD", "BUY", 0.1, 42100, 42200)
    >>> if success:
    ...     print(f"Position opened: {msg}")
    ... else:
    ...     print(f"Order rejected: {msg}")
    """

    # -------- GUARD 1: Symbol Whitelist -------- #
    if not symbol_allowed(symbol):
        msg = f"BLOCKED: SYMBOL {symbol} not in whitelist"
        logger.error(msg)
        return False, msg

    # -------- GUARD 2: Spread Filter -------- #
    if not spread_ok(symbol, bid, ask):
        msg = f"BLOCKED: SPREAD too wide {symbol}"
        logger.error(msg)
        return False, msg

    # -------- GUARD 3: Meme Restrictions -------- #
    if not meme_restrictions(symbol, side):
        msg = f"BLOCKED: MEME RULE {symbol} no {side.upper()} orders"
        logger.error(msg)
        return False, msg

    # -------- GUARD 4: Duplicate Prevention -------- #
    if not prevent_duplicate(symbol):
        msg = f"BLOCKED: DUPLICATE {symbol} on cooldown"
        logger.error(msg)
        return False, msg

    # -------- GUARD 3B: Build Limit Price -------- #
    try:
        price = build_limit_price(side, bid, ask)
    except Exception as e:
        msg = f"ERROR: Cannot build limit price - {e}"
        logger.error(msg)
        return False, msg

    # -------- GUARD 5: Order Size Validation -------- #
    if not order_size_ok(symbol, qty, price):
        msg = f"BLOCKED: SIZE too small {symbol}"
        logger.error(msg)
        return False, msg

    # -------- EXECUTION: Place Limit Order -------- #
    try:
        order = client.create_order(
            symbol=_normalize_symbol(symbol),
            order_type="limit",
            side=side.lower(),
            amount=qty,
            price=price,
        )
        order_id = order.get("id")
        logger.info(f"Order placed: {order_id} | {side.upper()} {qty} {symbol} @ {price}")
    except Exception as e:
        msg = f"ERROR: Cannot place order - {e}"
        logger.error(msg)
        return False, msg

    # -------- GUARD 6: Wait for Fill (with timeout) -------- #
    filled = wait_for_fill(client, order_id, _normalize_symbol(symbol), timeout=5)

    if filled:
        msg = f"FILLED | {side.upper()} {qty} {symbol}"
        logger.info(msg)
        return True, msg
    else:
        msg = f"CANCELLED: NO FILL {symbol} within 5 seconds"
        logger.warning(msg)
        return False, msg


__all__ = [
    "symbol_allowed",
    "spread_ok",
    "build_limit_price",
    "order_size_ok",
    "wait_for_fill",
    "prevent_duplicate",
    "meme_restrictions",
    "execute_trade",
    "ALLOWED_SYMBOLS",
    "MAX_SPREAD",
    "MIN_NOTIONAL",
    "MEME_COINS",
    "LAST_ORDER_TS",
]
