"""
Portfolio Manager - Tracks positions, balances, and performance metrics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import threading

from ..utils.logger import get_logger

logger = get_logger(__name__)


class Position:
    """Represents a trading position"""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        broker: str,
        timestamp: Optional[datetime] = None
    ):
        self.symbol = symbol
        self.side = side  # 'long' or 'short'
        self.entry_price = Decimal(str(entry_price))
        self.quantity = Decimal(str(quantity))
        self.broker = broker
        self.timestamp = timestamp or datetime.utcnow()
        self.realized_pnl = Decimal('0')
        self.stop_loss: Optional[Decimal] = None
        self.take_profit: Optional[Decimal] = None
        self.order_id: Optional[str] = None
        
    def get_unrealized_pnl(self, current_price: float) -> Decimal:
        """Calculate unrealized profit/loss"""
        current = Decimal(str(current_price))
        quantity = self.quantity
        
        if self.side == 'long':
            pnl = (current - self.entry_price) * quantity
        else:  # short
            pnl = (self.entry_price - current) * quantity
            
        return pnl
    
    def get_pnl_percentage(self, current_price: float) -> Decimal:
        """Calculate PnL as percentage"""
        pnl = self.get_unrealized_pnl(current_price)
        entry_value = self.entry_price * self.quantity
        
        if entry_value == 0:
            return Decimal('0')
            
        return (pnl / entry_value) * Decimal('100')
    
    def update_realized_pnl(self, close_price: float, close_quantity: float):
        """Update realized PnL when position is closed (partial or full)"""
        close_qty = Decimal(str(close_quantity))
        close_px = Decimal(str(close_price))
        
        if self.side == 'long':
            pnl = (close_px - self.entry_price) * close_qty
        else:
            pnl = (self.entry_price - close_px) * close_qty
            
        self.realized_pnl += pnl
        self.quantity -= close_qty
        
        logger.info(
            f"Position updated: {self.symbol} | Closed {close_qty} @ {close_px} | "
            f"PnL: {pnl} | Remaining: {self.quantity}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary"""
        return {
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': float(self.entry_price),
            'quantity': float(self.quantity),
            'broker': self.broker,
            'timestamp': self.timestamp.isoformat(),
            'realized_pnl': float(self.realized_pnl),
            'stop_loss': float(self.stop_loss) if self.stop_loss else None,
            'take_profit': float(self.take_profit) if self.take_profit else None,
            'order_id': self.order_id
        }


class PortfolioManager:
    """
    Manages portfolio positions, balances, and performance tracking.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, mode: str = 'paper', initial_capital: float = 10000.0):
        """
        Initialize the portfolio manager
        
        Args:
            mode: Trading mode ('paper' or 'live')
            initial_capital: Initial capital for paper trading
        """
        self.mode = mode
        self.initial_capital = Decimal(str(initial_capital))
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Positions tracking
        self._positions: Dict[str, Position] = {}  # symbol -> Position
        
        # Balance tracking (per currency/asset)
        self._balances: Dict[str, Decimal] = {'USD': self.initial_capital}
        
        # Performance metrics
        self._total_trades = 0
        self._winning_trades = 0
        self._losing_trades = 0
        self._total_pnl = Decimal('0')
        self._peak_balance = self.initial_capital
        self._max_drawdown = Decimal('0')
        
        # Trade history
        self._trade_history: List[Dict[str, Any]] = []
        
        logger.info(
            f"Portfolio manager initialized | Mode: {mode} | "
            f"Initial capital: {initial_capital}"
        )
    
    def add_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        broker: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        order_id: Optional[str] = None
    ) -> bool:
        """
        Add a new position to the portfolio
        
        Args:
            symbol: Trading symbol
            side: Position side ('long' or 'short')
            entry_price: Entry price
            quantity: Position quantity
            broker: Broker name
            stop_loss: Stop loss price
            take_profit: Take profit price
            order_id: Associated order ID
            
        Returns:
            True if position added successfully
        """
        with self._lock:
            try:
                # Check if position already exists
                if symbol in self._positions:
                    logger.warning(f"Position already exists for {symbol}")
                    # Could implement position averaging here
                    return False
                
                position = Position(symbol, side, entry_price, quantity, broker)
                position.stop_loss = Decimal(str(stop_loss)) if stop_loss else None
                position.take_profit = Decimal(str(take_profit)) if take_profit else None
                position.order_id = order_id
                
                self._positions[symbol] = position
                
                logger.info(
                    f"Position opened: {symbol} | Side: {side} | "
                    f"Price: {entry_price} | Qty: {quantity}"
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Error adding position for {symbol}: {e}", exc_info=True)
                return False
    
    def close_position(
        self,
        symbol: str,
        close_price: float,
        close_quantity: Optional[float] = None
    ) -> Optional[Decimal]:
        """
        Close a position (fully or partially)
        
        Args:
            symbol: Trading symbol
            close_price: Close price
            close_quantity: Quantity to close (None = full position)
            
        Returns:
            Realized PnL or None if error
        """
        with self._lock:
            try:
                if symbol not in self._positions:
                    logger.warning(f"No position found for {symbol}")
                    return None
                
                position = self._positions[symbol]
                
                # Determine close quantity
                if close_quantity is None:
                    qty_to_close = float(position.quantity)
                else:
                    qty_to_close = min(close_quantity, float(position.quantity))
                
                # Calculate PnL
                position.update_realized_pnl(close_price, qty_to_close)
                pnl = position.realized_pnl
                
                # Update portfolio metrics
                self._total_trades += 1
                self._total_pnl += pnl
                
                if pnl > 0:
                    self._winning_trades += 1
                else:
                    self._losing_trades += 1
                
                # Record trade
                self._record_trade(position, close_price, qty_to_close, pnl)
                
                # Remove position if fully closed
                if position.quantity <= 0:
                    del self._positions[symbol]
                    logger.info(f"Position fully closed: {symbol} | PnL: {pnl}")
                else:
                    logger.info(
                        f"Position partially closed: {symbol} | PnL: {pnl} | "
                        f"Remaining: {position.quantity}"
                    )
                
                # Update drawdown
                self._update_drawdown()
                
                return pnl
                
            except Exception as e:
                logger.error(f"Error closing position for {symbol}: {e}", exc_info=True)
                return None
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol"""
        with self._lock:
            return self._positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Get all open positions"""
        with self._lock:
            return self._positions.copy()
    
    def has_position(self, symbol: str) -> bool:
        """Check if position exists for symbol"""
        with self._lock:
            return symbol in self._positions
    
    def get_position_count(self) -> int:
        """Get number of open positions"""
        with self._lock:
            return len(self._positions)
    
    def update_balance(self, currency: str, amount: float):
        """Update balance for a currency"""
        with self._lock:
            current = self._balances.get(currency, Decimal('0'))
            self._balances[currency] = current + Decimal(str(amount))
            
            logger.debug(f"Balance updated: {currency} = {self._balances[currency]}")
    
    def get_balance(self, currency: str = 'USD') -> float:
        """Get balance for a currency"""
        with self._lock:
            return float(self._balances.get(currency, Decimal('0')))
    
    def get_total_value(self, current_prices: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate total portfolio value including unrealized PnL
        
        Args:
            current_prices: Dictionary of symbol -> current price
            
        Returns:
            Total portfolio value
        """
        with self._lock:
            total = Decimal('0')
            
            # Add cash balances
            for balance in self._balances.values():
                total += balance
            
            # Add unrealized PnL from open positions
            if current_prices:
                for symbol, position in self._positions.items():
                    if symbol in current_prices:
                        unrealized_pnl = position.get_unrealized_pnl(current_prices[symbol])
                        total += unrealized_pnl
            
            return float(total)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get portfolio performance metrics"""
        with self._lock:
            win_rate = 0.0
            if self._total_trades > 0:
                win_rate = (self._winning_trades / self._total_trades) * 100
            
            current_value = self.get_total_value()
            total_return = float(
                ((Decimal(str(current_value)) - self.initial_capital) / 
                 self.initial_capital) * Decimal('100')
            )
            
            return {
                'total_trades': self._total_trades,
                'winning_trades': self._winning_trades,
                'losing_trades': self._losing_trades,
                'win_rate': win_rate,
                'total_pnl': float(self._total_pnl),
                'max_drawdown': float(self._max_drawdown),
                'initial_capital': float(self.initial_capital),
                'current_value': current_value,
                'total_return': total_return,
                'open_positions': len(self._positions)
            }
    
    def get_trade_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get trade history"""
        with self._lock:
            if limit:
                return self._trade_history[-limit:]
            return self._trade_history.copy()
    
    def _record_trade(
        self,
        position: Position,
        close_price: float,
        quantity: float,
        pnl: Decimal
    ):
        """Record a completed trade"""
        trade = {
            'symbol': position.symbol,
            'side': position.side,
            'entry_price': float(position.entry_price),
            'exit_price': close_price,
            'quantity': quantity,
            'pnl': float(pnl),
            'pnl_percentage': float(
                (pnl / (position.entry_price * Decimal(str(quantity)))) * Decimal('100')
            ),
            'entry_time': position.timestamp.isoformat(),
            'exit_time': datetime.utcnow().isoformat(),
            'broker': position.broker
        }
        
        self._trade_history.append(trade)
    
    def _update_drawdown(self):
        """Update maximum drawdown"""
        current_value = Decimal(str(self.get_total_value()))
        
        if current_value > self._peak_balance:
            self._peak_balance = current_value
        
        if self._peak_balance > 0:
            drawdown = ((self._peak_balance - current_value) / self._peak_balance) * Decimal('100')
            if drawdown > self._max_drawdown:
                self._max_drawdown = drawdown
    
    def reset(self):
        """Reset portfolio (for paper trading)"""
        with self._lock:
            if self.mode != 'paper':
                logger.error("Cannot reset portfolio in live mode")
                return
            
            self._positions.clear()
            self._balances = {'USD': self.initial_capital}
            self._total_trades = 0
            self._winning_trades = 0
            self._losing_trades = 0
            self._total_pnl = Decimal('0')
            self._peak_balance = self.initial_capital
            self._max_drawdown = Decimal('0')
            self._trade_history.clear()
            
            logger.info("Portfolio reset to initial state")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio state to dictionary"""
        with self._lock:
            return {
                'mode': self.mode,
                'balances': {k: float(v) for k, v in self._balances.items()},
                'positions': {k: v.to_dict() for k, v in self._positions.items()},
                'performance': self.get_performance_metrics(),
                'timestamp': datetime.utcnow().isoformat()
            }
