"""
Enhanced Risk Engine V2 - Advanced position sizing with exposure caps
Implements:
- Per-asset risk tiers
- Portfolio exposure caps
- Loss streak tracking
- Symbol-specific rules (memes, majors)
"""

from typing import Dict, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import threading

from ..utils.logger import get_logger

logger = get_logger(__name__)


# Asset-specific risk configuration
ASSET_RISK_TIERS = {
    "BTC": {"max_risk_pct": 0.75, "min_spread": 0.0005, "max_position_notional": 5000},
    "ETH": {"max_risk_pct": 0.75, "min_spread": 0.0005, "max_position_notional": 3000},
    "XRP": {"max_risk_pct": 0.50, "min_spread": 0.0008, "max_position_notional": 500},
    "DOGE": {"max_risk_pct": 0.30, "min_spread": 0.0012, "max_position_notional": 200, "gold_mode": True},
    "SHIB": {"max_risk_pct": 0.20, "min_spread": 0.0020, "max_position_notional": 100, "gold_mode": True},
    "TRUMP": {"max_risk_pct": 0.10, "min_spread": 0.0025, "max_position_notional": 50, "gold_mode": True},
}

# Meme coins - special handling
MEME_COINS = {"DOGE", "SHIB", "TRUMP"}


class RiskEngineV2:
    """
    Enhanced risk management with:
    - Per-asset risk allocation
    - Portfolio-level exposure limits
    - Loss streak detection
    - Consecutive trade limits
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize enhanced risk engine"""
        self._lock = threading.RLock()
        
        self.config = config or {}
        
        # Basic limits
        self.account_balance = Decimal(str(self.config.get('account_balance', 10000)))
        self.portfolio_max_risk = Decimal(str(self.config.get('portfolio_max_risk_pct', 3.0)))
        self.max_open_positions = self.config.get('max_open_positions', 6)
        self.max_consecutive_losses = self.config.get('max_consecutive_losses', 5)
        
        # Daily limits
        self.max_daily_loss = Decimal(str(self.config.get('max_daily_loss_pct', 5.0)))
        
        # Trading state
        self._open_positions: Dict[str, Dict[str, Any]] = {}  # symbol -> position info
        self._position_history: list = []  # Historical trades
        self._daily_loss = Decimal('0')
        self._daily_start_balance = self.account_balance
        self._last_reset_date = datetime.utcnow().date()
        
        self._consecutive_losses = 0
        self._trading_halted = False
        self._halt_reason: Optional[str] = None
        
        logger.info(
            f"RiskEngineV2 initialized | Balance: ${self.account_balance} | "
            f"Max daily loss: {self.max_daily_loss}% | "
            f"Portfolio risk: {self.portfolio_max_risk}%"
        )
    
    def _get_asset_name(self, symbol: str) -> str:
        """Extract asset name from symbol (e.g., 'BTC_USD' -> 'BTC')"""
        return symbol.split('_')[0].split('/')[0]
    
    def _check_daily_reset(self):
        """Reset daily counters if needed"""
        today = datetime.utcnow().date()
        if today > self._last_reset_date:
            logger.info(
                f"Daily reset: balance ${self.account_balance} | "
                f"daily loss: ${self._daily_loss}"
            )
            self._daily_loss = Decimal('0')
            self._daily_start_balance = self.account_balance
            self._last_reset_date = today
    
    def can_open_position(
        self,
        symbol: str,
        direction: str,
        qty: float,
        entry_price: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive check: can we open a new position?
        
        Checks:
        1. Not currently in trade for this symbol
        2. Not in cooldown
        3. Within risk per asset
        4. Within portfolio exposure
        5. Not trading halted
        6. Within daily loss limit
        7. Not exceeded consecutive losses
        8. Meme coin rules
        """
        with self._lock:
            asset = self._get_asset_name(symbol)
            
            # Check if trading halted
            if self._trading_halted:
                return False, f"Trading halted: {self._halt_reason}"
            
            # Check daily reset
            self._check_daily_reset()
            
            # Check if already in trade for this symbol
            if symbol in self._open_positions:
                return False, f"{symbol}: Position already open"
            
            # Check consecutive losses
            if self._consecutive_losses >= self.max_consecutive_losses:
                return False, (
                    f"Max consecutive losses reached ({self.max_consecutive_losses}). "
                    f"Trading halted for safety."
                )
            
            # Check daily loss
            daily_loss_pct = (self._daily_loss / self._daily_start_balance * 100)
            if daily_loss_pct >= float(self.max_daily_loss):
                return False, (
                    f"Daily loss limit reached ({daily_loss_pct:.2f}% >= {self.max_daily_loss}%)"
                )
            
            # Check max open positions
            if len(self._open_positions) >= self.max_open_positions:
                return False, f"Max open positions reached ({self.max_open_positions})"
            
            # Get asset-specific limits
            asset_config = ASSET_RISK_TIERS.get(asset, {})
            max_risk_pct = Decimal(str(asset_config.get('max_risk_pct', 0.75)))
            
            # Calculate position value
            position_value = Decimal(str(qty * entry_price))
            
            # Check position size limit
            max_position = Decimal(str(asset_config.get('max_position_notional', 5000)))
            if position_value > max_position:
                return False, (
                    f"{symbol}: Position size ${position_value} exceeds "
                    f"max allowed ${max_position}"
                )
            
            # Check asset-specific risk
            asset_risk_value = self.account_balance * (max_risk_pct / Decimal('100'))
            if position_value > asset_risk_value:
                return False, (
                    f"{symbol}: Risk ${position_value} exceeds "
                    f"asset limit ${asset_risk_value} ({max_risk_pct}%)"
                )
            
            # Check portfolio exposure
            total_exposure = sum(
                Decimal(str(pos['value'])) for pos in self._open_positions.values()
            ) + position_value
            
            max_portfolio_risk = self.account_balance * (self.portfolio_max_risk / Decimal('100'))
            if total_exposure > max_portfolio_risk:
                return False, (
                    f"{symbol}: Portfolio exposure ${total_exposure} exceeds "
                    f"limit ${max_portfolio_risk} ({self.portfolio_max_risk}%)"
                )
            
            # Check meme coin rules
            if asset in MEME_COINS and direction == "SELL":
                return False, (
                    f"{symbol}: Meme coin restriction - no SELL orders allowed "
                    f"(gold mode: BUY only)"
                )
            
            logger.debug(
                f"{symbol} position approved | {direction} {qty} @ ${entry_price:.2f} | "
                f"Value: ${position_value:.2f} | Exposure: ${total_exposure:.2f}"
            )
            
            return True, None
    
    def open_position(
        self,
        symbol: str,
        direction: str,
        qty: float,
        entry_price: float
    ) -> Dict[str, Any]:
        """
        Record a newly opened position
        """
        with self._lock:
            can_open, reason = self.can_open_position(symbol, direction, qty, entry_price)
            if not can_open:
                raise ValueError(reason or f"Cannot open position for {symbol}")
            
            position = {
                "symbol": symbol,
                "direction": direction,
                "qty": qty,
                "entry_price": entry_price,
                "value": qty * entry_price,
                "opened_at": datetime.utcnow(),
                "opened_candle": 0,
            }
            
            self._open_positions[symbol] = position
            logger.info(f"{symbol} position opened: {direction} {qty} @ ${entry_price:.2f}")
            
            return position
    
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str
    ) -> Dict[str, Any]:
        """
        Record a closed position and calculate P&L
        """
        with self._lock:
            if symbol not in self._open_positions:
                raise ValueError(f"No open position for {symbol}")
            
            position = self._open_positions[symbol]
            
            # Calculate P&L
            if position['direction'] == 'BUY':
                pnl = (exit_price - position['entry_price']) * position['qty']
            else:  # SELL
                pnl = (position['entry_price'] - exit_price) * position['qty']
            
            pnl_decimal = Decimal(str(pnl))
            
            # Update daily loss if loss
            if pnl < 0:
                self._daily_loss += abs(pnl_decimal)
                self._consecutive_losses += 1
            else:
                self._consecutive_losses = 0
            
            # Update account balance
            self.account_balance += pnl_decimal
            
            closed_position = {
                **position,
                "exit_price": exit_price,
                "exit_reason": reason,
                "closed_at": datetime.utcnow(),
                "pnl": pnl,
                "pnl_pct": (pnl / position['value'] * 100) if position['value'] > 0 else 0,
            }
            
            self._position_history.append(closed_position)
            del self._open_positions[symbol]
            
            logger.info(
                f"{symbol} position closed | Reason: {reason} | "
                f"PnL: ${pnl:.2f} ({closed_position['pnl_pct']:.2f}%) | "
                f"Balance: ${self.account_balance:.2f}"
            )
            
            return closed_position
    
    def get_current_exposure(self) -> Dict[str, Any]:
        """Get current portfolio exposure"""
        with self._lock:
            total_exposure = Decimal('0')
            exposure_by_asset: Dict[str, Decimal] = {}
            open_positions = []
            
            for symbol, pos in self._open_positions.items():
                asset = self._get_asset_name(symbol)
                value = Decimal(str(pos['value']))
                total_exposure += value
                exposure_by_asset[asset] = exposure_by_asset.get(asset, Decimal('0')) + value
                open_positions.append({
                    "symbol": symbol,
                    "direction": pos.get("direction"),
                    "qty": pos.get("qty"),
                    "entry_price": pos.get("entry_price"),
                    "value": float(value),
                })
            
            exposure_pct = 0.0
            if self.account_balance > 0:
                exposure_pct = float(total_exposure / self.account_balance * Decimal('100'))
            
            return {
                "total_exposure": float(total_exposure),
                "exposure_pct": exposure_pct,
                "exposure_by_asset": {k: float(v) for k, v in exposure_by_asset.items()},
                "num_positions": len(self._open_positions),
                "open_positions": open_positions,
                "max_allowed": float(self.account_balance * self.portfolio_max_risk / Decimal('100')),
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get risk statistics"""
        with self._lock:
            self._check_daily_reset()
            
            if not self._position_history:
                return {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "consecutive_losses": self._consecutive_losses,
                    "daily_loss": 0.0,
                }
            
            total = len(self._position_history)
            wins = len([p for p in self._position_history if p['pnl'] > 0])
            losses = len([p for p in self._position_history if p['pnl'] < 0])
            total_pnl = sum(p['pnl'] for p in self._position_history)
            
            return {
                "total_trades": total,
                "winning_trades": wins,
                "losing_trades": losses,
                "win_rate": (wins / total * 100) if total > 0 else 0.0,
                "total_pnl": total_pnl,
                "consecutive_losses": self._consecutive_losses,
                "daily_loss": float(self._daily_loss),
                "current_balance": float(self.account_balance),
            }
    
    def halt_trading(self, reason: str):
        """Emergency halt trading"""
        with self._lock:
            self._trading_halted = True
            self._halt_reason = reason
            logger.error(f"TRADING HALTED: {reason}")


__all__ = ["RiskEngineV2", "ASSET_RISK_TIERS", "MEME_COINS"]
