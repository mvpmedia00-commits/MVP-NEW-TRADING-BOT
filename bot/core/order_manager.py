"""
Order Manager - Handles order creation, execution, and tracking
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import threading
import time

from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    FAILED = "failed"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


class Order:
    """Represents a trading order"""
    
    def __init__(
        self,
        symbol: str,
        order_type: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        broker: str = "",
        order_id: Optional[str] = None
    ):
        self.order_id = order_id or f"ORD_{int(time.time() * 1000)}"
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.broker = broker
        
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0.0
        self.average_fill_price = 0.0
        self.commission = 0.0
        
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.filled_at: Optional[datetime] = None
        
        self.broker_order_id: Optional[str] = None
        self.error_message: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def update_status(self, status: OrderStatus, message: Optional[str] = None):
        """Update order status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if message:
            self.error_message = message
        
        if status == OrderStatus.FILLED:
            self.filled_at = datetime.utcnow()
    
    def update_fill(self, filled_qty: float, fill_price: float, commission: float = 0.0):
        """Update order fill information"""
        self.filled_quantity = filled_qty
        self.average_fill_price = fill_price
        self.commission += commission
        self.updated_at = datetime.utcnow()
        
        if self.filled_quantity >= self.quantity:
            self.update_status(OrderStatus.FILLED)
        elif self.filled_quantity > 0:
            self.update_status(OrderStatus.PARTIALLY_FILLED)
    
    def is_active(self) -> bool:
        """Check if order is active (not terminal state)"""
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.OPEN,
            OrderStatus.PARTIALLY_FILLED
        ]
    
    def is_filled(self) -> bool:
        """Check if order is completely filled"""
        return self.status == OrderStatus.FILLED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary"""
        return {
            'order_id': self.order_id,
            'broker_order_id': self.broker_order_id,
            'symbol': self.symbol,
            'order_type': self.order_type,
            'side': self.side,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'broker': self.broker,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'average_fill_price': self.average_fill_price,
            'commission': self.commission,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class OrderManager:
    """
    Manages order creation, execution, and lifecycle.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, mode: str = 'paper'):
        """
        Initialize the order manager
        
        Args:
            mode: Trading mode ('paper' or 'live')
        """
        self.mode = mode
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Order tracking
        self._orders: Dict[str, Order] = {}  # order_id -> Order
        self._broker_order_map: Dict[str, str] = {}  # broker_order_id -> order_id
        
        # Order history
        self._order_history: List[Order] = []
        
        # Statistics
        self._total_orders = 0
        self._filled_orders = 0
        self._cancelled_orders = 0
        self._rejected_orders = 0
        
        logger.info(f"Order manager initialized | Mode: {mode}")
    
    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        broker: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Order]:
        """
        Create a new order
        
        Args:
            symbol: Trading symbol
            order_type: Order type (market, limit, etc.)
            side: Order side (buy/sell)
            quantity: Order quantity
            price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            broker: Broker name
            metadata: Additional metadata
            
        Returns:
            Created Order object or None if error
        """
        with self._lock:
            try:
                # Validate inputs
                if quantity <= 0:
                    logger.error(f"Invalid quantity: {quantity}")
                    return None
                
                if order_type == 'limit' and not price:
                    logger.error("Limit order requires price")
                    return None
                
                # Create order
                order = Order(
                    symbol=symbol,
                    order_type=order_type,
                    side=side,
                    quantity=quantity,
                    price=price,
                    stop_price=stop_price,
                    broker=broker
                )
                
                if metadata:
                    order.metadata = metadata
                
                # Store order
                self._orders[order.order_id] = order
                self._total_orders += 1
                
                logger.info(
                    f"Order created: {order.order_id} | {symbol} | "
                    f"{side} {quantity} @ {price or 'market'}"
                )
                
                return order
                
            except Exception as e:
                logger.error(f"Error creating order: {e}", exc_info=True)
                return None
    
    def submit_order(self, order_id: str, broker_order_id: str) -> bool:
        """
        Mark order as submitted to broker
        
        Args:
            order_id: Internal order ID
            broker_order_id: Broker's order ID
            
        Returns:
            True if successful
        """
        with self._lock:
            try:
                order = self._orders.get(order_id)
                if not order:
                    logger.error(f"Order not found: {order_id}")
                    return False
                
                order.broker_order_id = broker_order_id
                order.update_status(OrderStatus.SUBMITTED)
                
                # Map broker order ID to internal ID
                self._broker_order_map[broker_order_id] = order_id
                
                logger.info(
                    f"Order submitted: {order_id} | Broker ID: {broker_order_id}"
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Error submitting order: {e}", exc_info=True)
                return False
    
    def update_order_status(
        self,
        order_id: str,
        status: str,
        filled_quantity: Optional[float] = None,
        fill_price: Optional[float] = None,
        commission: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update order status and fill information
        
        Args:
            order_id: Order ID (internal or broker)
            status: New status
            filled_quantity: Filled quantity
            fill_price: Fill price
            commission: Commission paid
            error_message: Error message if any
            
        Returns:
            True if successful
        """
        with self._lock:
            try:
                # Get order (handle both internal and broker IDs)
                order = self._get_order_by_any_id(order_id)
                if not order:
                    logger.warning(f"Order not found for update: {order_id}")
                    return False
                
                # Convert status string to enum
                try:
                    status_enum = OrderStatus(status.lower())
                except ValueError:
                    logger.error(f"Invalid status: {status}")
                    return False
                
                # Update fill info if provided
                if filled_quantity is not None and fill_price is not None:
                    order.update_fill(
                        filled_quantity,
                        fill_price,
                        commission or 0.0
                    )
                else:
                    order.update_status(status_enum, error_message)
                
                # Update statistics
                if status_enum == OrderStatus.FILLED:
                    self._filled_orders += 1
                elif status_enum == OrderStatus.CANCELLED:
                    self._cancelled_orders += 1
                elif status_enum == OrderStatus.REJECTED:
                    self._rejected_orders += 1
                
                # Move to history if terminal state
                if not order.is_active():
                    self._order_history.append(order)
                
                logger.info(
                    f"Order updated: {order.order_id} | Status: {status} | "
                    f"Filled: {order.filled_quantity}/{order.quantity}"
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Error updating order: {e}", exc_info=True)
                return False
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Mark order as cancelled
        
        Args:
            order_id: Order ID
            
        Returns:
            True if successful
        """
        with self._lock:
            return self.update_order_status(order_id, OrderStatus.CANCELLED.value)
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get order by ID
        
        Args:
            order_id: Order ID (internal or broker)
            
        Returns:
            Order object or None
        """
        with self._lock:
            return self._get_order_by_any_id(order_id)
    
    def get_active_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get all active orders
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of active orders
        """
        with self._lock:
            active = [
                order for order in self._orders.values()
                if order.is_active()
            ]
            
            if symbol:
                active = [o for o in active if o.symbol == symbol]
            
            return active
    
    def get_all_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get all orders (active and history)
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of all orders
        """
        with self._lock:
            all_orders = list(self._orders.values()) + self._order_history
            
            if symbol:
                all_orders = [o for o in all_orders if o.symbol == symbol]
            
            return sorted(all_orders, key=lambda x: x.created_at, reverse=True)
    
    def get_order_history(
        self,
        symbol: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Order]:
        """
        Get order history
        
        Args:
            symbol: Optional symbol filter
            limit: Maximum number of orders to return
            
        Returns:
            List of historical orders
        """
        with self._lock:
            history = self._order_history.copy()
            
            if symbol:
                history = [o for o in history if o.symbol == symbol]
            
            if limit:
                history = history[-limit:]
            
            return history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get order statistics"""
        with self._lock:
            active_count = len([o for o in self._orders.values() if o.is_active()])
            
            fill_rate = 0.0
            if self._total_orders > 0:
                fill_rate = (self._filled_orders / self._total_orders) * 100
            
            return {
                'total_orders': self._total_orders,
                'active_orders': active_count,
                'filled_orders': self._filled_orders,
                'cancelled_orders': self._cancelled_orders,
                'rejected_orders': self._rejected_orders,
                'fill_rate': fill_rate,
                'historical_orders': len(self._order_history)
            }
    
    def cleanup_old_orders(self, days: int = 7):
        """
        Remove old orders from history
        
        Args:
            days: Number of days to keep
        """
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            initial_count = len(self._order_history)
            self._order_history = [
                order for order in self._order_history
                if order.updated_at > cutoff_time
            ]
            
            removed = initial_count - len(self._order_history)
            if removed > 0:
                logger.info(f"Cleaned up {removed} old orders")
    
    def _get_order_by_any_id(self, order_id: str) -> Optional[Order]:
        """Get order by internal or broker order ID"""
        # Try internal ID first
        order = self._orders.get(order_id)
        if order:
            return order
        
        # Try broker ID
        internal_id = self._broker_order_map.get(order_id)
        if internal_id:
            return self._orders.get(internal_id)
        
        # Search in history
        for order in self._order_history:
            if order.order_id == order_id or order.broker_order_id == order_id:
                return order
        
        return None
    
    def reset(self):
        """Reset order manager (for testing)"""
        with self._lock:
            if self.mode != 'paper':
                logger.error("Cannot reset order manager in live mode")
                return
            
            self._orders.clear()
            self._broker_order_map.clear()
            self._order_history.clear()
            self._total_orders = 0
            self._filled_orders = 0
            self._cancelled_orders = 0
            self._rejected_orders = 0
            
            logger.info("Order manager reset")


from datetime import timedelta
