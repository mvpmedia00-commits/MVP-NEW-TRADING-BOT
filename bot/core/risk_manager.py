"""
Risk Manager - Manages risk parameters, position sizing, and loss limits
"""

from typing import Dict, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
import threading

from ..utils.logger import get_logger

logger = get_logger(__name__)


class RiskManager:
    """
    Manages risk controls for the trading bot.
    Enforces position sizing, max loss limits, and risk constraints.
    """
    
    def __init__(self, config: Dict[str, Any], mode: str = 'paper'):
        """
        Initialize the risk manager
        
        Args:
            config: Risk management configuration
            mode: Trading mode ('paper' or 'live')
        """
        self.mode = mode
        self.config = config
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Risk parameters
        self.max_position_size = Decimal(str(config.get('max_position_size', 1000)))
        self.max_daily_loss = Decimal(str(config.get('max_daily_loss', 500)))
        self.max_open_positions = config.get('max_open_positions', 5)
        self.position_size_type = config.get('position_size_type', 'fixed')
        self.emergency_stop_loss = Decimal(str(config.get('emergency_stop_loss', 10.0)))
        
        # Position sizing parameters
        self.risk_per_trade = Decimal(str(config.get('risk_per_trade', 1.0)))  # % of capital
        self.max_leverage = Decimal(str(config.get('max_leverage', 1.0)))
        
        # Daily tracking
        self._daily_loss = Decimal('0')
        self._daily_trades = 0
        self._last_reset_date = datetime.utcnow().date()
        self._trading_halted = False
        self._halt_reason: Optional[str] = None
        
        # Symbol-specific risk (optional)
        self._symbol_limits: Dict[str, Dict[str, Any]] = {}
        
        logger.info(
            f"Risk manager initialized | Mode: {mode} | "
            f"Max position: {self.max_position_size} | "
            f"Max daily loss: {self.max_daily_loss}"
        )
    
    def validate_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        current_positions: int,
        account_balance: float,
        portfolio_value: Optional[float] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if an order meets risk management criteria
        
        Args:
            symbol: Trading symbol
            side: Order side ('buy' or 'sell')
            quantity: Order quantity
            price: Order price
            current_positions: Number of current open positions
            account_balance: Current account balance
            portfolio_value: Total portfolio value (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        with self._lock:
            try:
                # Check if trading is halted
                if self._trading_halted:
                    return False, f"Trading halted: {self._halt_reason}"
                
                # Reset daily tracking if new day
                self._check_daily_reset()
                
                # Check max open positions
                if current_positions >= self.max_open_positions:
                    return False, f"Max open positions reached ({self.max_open_positions})"
                
                # Calculate order value
                order_value = Decimal(str(quantity)) * Decimal(str(price))
                
                # Check position size limit
                if order_value > self.max_position_size:
                    return False, (
                        f"Order value {order_value} exceeds max position size "
                        f"{self.max_position_size}"
                    )
                
                # Check account balance
                balance = Decimal(str(account_balance))
                if order_value > balance:
                    return False, (
                        f"Insufficient balance: {balance} < {order_value}"
                    )
                
                # Check symbol-specific limits
                symbol_check = self._validate_symbol_limits(symbol, order_value)
                if not symbol_check[0]:
                    return symbol_check
                
                # Check if order would exceed risk per trade
                if portfolio_value:
                    portfolio = Decimal(str(portfolio_value))
                    max_risk_value = portfolio * (self.risk_per_trade / Decimal('100'))
                    
                    if order_value > max_risk_value:
                        return False, (
                            f"Order value {order_value} exceeds risk per trade "
                            f"{max_risk_value} ({self.risk_per_trade}%)"
                        )
                
                logger.debug(
                    f"Order validated: {symbol} | {side} | "
                    f"{quantity} @ {price} | Value: {order_value}"
                )
                
                return True, None
                
            except Exception as e:
                logger.error(f"Error validating order: {e}", exc_info=True)
                return False, f"Validation error: {str(e)}"
    
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_price: Optional[float],
        account_balance: float,
        portfolio_value: Optional[float] = None
    ) -> float:
        """
        Calculate appropriate position size based on risk parameters
        
        Args:
            symbol: Trading symbol
            entry_price: Intended entry price
            stop_loss_price: Stop loss price (optional)
            account_balance: Current account balance
            portfolio_value: Total portfolio value
            
        Returns:
            Recommended position size (quantity)
        """
        with self._lock:
            try:
                balance = Decimal(str(account_balance))
                entry = Decimal(str(entry_price))
                
                if self.position_size_type == 'fixed':
                    # Fixed dollar amount
                    position_value = min(self.max_position_size, balance)
                    quantity = position_value / entry
                    
                elif self.position_size_type == 'percentage':
                    # Percentage of portfolio
                    portfolio = Decimal(str(portfolio_value or account_balance))
                    position_value = portfolio * (self.risk_per_trade / Decimal('100'))
                    position_value = min(position_value, self.max_position_size)
                    quantity = position_value / entry
                    
                elif self.position_size_type == 'risk_based' and stop_loss_price:
                    # Based on risk (distance to stop loss)
                    stop_loss = Decimal(str(stop_loss_price))
                    risk_per_unit = abs(entry - stop_loss)
                    
                    if risk_per_unit == 0:
                        logger.warning("Stop loss equals entry price, using fixed sizing")
                        position_value = min(self.max_position_size, balance)
                        quantity = position_value / entry
                    else:
                        # Risk amount per trade
                        portfolio = Decimal(str(portfolio_value or account_balance))
                        risk_amount = portfolio * (self.risk_per_trade / Decimal('100'))
                        
                        # Calculate position size
                        quantity = risk_amount / risk_per_unit
                        position_value = quantity * entry
                        
                        # Cap at max position size
                        if position_value > self.max_position_size:
                            quantity = self.max_position_size / entry
                else:
                    # Default to fixed
                    position_value = min(self.max_position_size, balance)
                    quantity = position_value / entry
                
                # Ensure we don't exceed account balance
                max_quantity = balance / entry
                quantity = min(quantity, max_quantity)
                
                logger.info(
                    f"Position size calculated: {symbol} | "
                    f"Qty: {quantity} | Value: {quantity * entry}"
                )
                
                return float(quantity)
                
            except Exception as e:
                logger.error(f"Error calculating position size: {e}", exc_info=True)
                return 0.0
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        side: str,
        atr: Optional[float] = None,
        percentage: Optional[float] = None
    ) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: Position side ('long' or 'short')
            atr: Average True Range (for ATR-based stops)
            percentage: Stop loss percentage (default from config)
            
        Returns:
            Stop loss price
        """
        try:
            entry = Decimal(str(entry_price))
            
            if atr:
                # ATR-based stop loss
                atr_multiplier = Decimal(str(self.config.get('atr_stop_multiplier', 2.0)))
                stop_distance = Decimal(str(atr)) * atr_multiplier
            else:
                # Percentage-based stop loss
                if percentage is None:
                    percentage = float(self.config.get('default_stop_loss_pct', 2.0))
                stop_distance = entry * (Decimal(str(percentage)) / Decimal('100'))
            
            if side == 'long':
                stop_loss = entry - stop_distance
            else:  # short
                stop_loss = entry + stop_distance
            
            return float(stop_loss)
            
        except Exception as e:
            logger.error(f"Error calculating stop loss: {e}", exc_info=True)
            return entry_price
    
    def calculate_take_profit(
        self,
        entry_price: float,
        side: str,
        risk_reward_ratio: Optional[float] = None,
        percentage: Optional[float] = None
    ) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            side: Position side ('long' or 'short')
            risk_reward_ratio: Risk/reward ratio (e.g., 2.0 for 1:2)
            percentage: Take profit percentage
            
        Returns:
            Take profit price
        """
        try:
            entry = Decimal(str(entry_price))
            
            if risk_reward_ratio:
                # Based on risk/reward ratio
                stop_pct = Decimal(str(self.config.get('default_stop_loss_pct', 2.0)))
                profit_pct = stop_pct * Decimal(str(risk_reward_ratio))
            else:
                # Percentage-based
                if percentage is None:
                    percentage = float(self.config.get('default_take_profit_pct', 4.0))
                profit_pct = Decimal(str(percentage))
            
            profit_distance = entry * (profit_pct / Decimal('100'))
            
            if side == 'long':
                take_profit = entry + profit_distance
            else:  # short
                take_profit = entry - profit_distance
            
            return float(take_profit)
            
        except Exception as e:
            logger.error(f"Error calculating take profit: {e}", exc_info=True)
            return entry_price
    
    def record_trade_result(self, pnl: float):
        """
        Record trade result and update daily tracking
        
        Args:
            pnl: Profit/loss from the trade
        """
        with self._lock:
            self._check_daily_reset()
            
            pnl_decimal = Decimal(str(pnl))
            self._daily_loss += pnl_decimal
            self._daily_trades += 1
            
            # Check if daily loss limit exceeded
            if abs(self._daily_loss) >= self.max_daily_loss:
                self._halt_trading(
                    f"Daily loss limit reached: {self._daily_loss} >= {self.max_daily_loss}"
                )
            
            logger.info(
                f"Trade recorded | PnL: {pnl} | Daily PnL: {self._daily_loss} | "
                f"Daily trades: {self._daily_trades}"
            )
    
    def check_emergency_stop(
        self,
        current_price: float,
        entry_price: float,
        side: str
    ) -> bool:
        """
        Check if emergency stop loss should trigger
        
        Args:
            current_price: Current market price
            entry_price: Position entry price
            side: Position side ('long' or 'short')
            
        Returns:
            True if emergency stop should trigger
        """
        try:
            current = Decimal(str(current_price))
            entry = Decimal(str(entry_price))
            
            if side == 'long':
                loss_pct = ((entry - current) / entry) * Decimal('100')
            else:
                loss_pct = ((current - entry) / entry) * Decimal('100')
            
            if loss_pct >= self.emergency_stop_loss:
                logger.warning(
                    f"Emergency stop triggered | Loss: {loss_pct}% >= "
                    f"{self.emergency_stop_loss}%"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking emergency stop: {e}", exc_info=True)
            return False
    
    def set_symbol_limit(self, symbol: str, max_position_value: float):
        """Set position limit for specific symbol"""
        with self._lock:
            self._symbol_limits[symbol] = {
                'max_position_value': Decimal(str(max_position_value))
            }
            logger.info(f"Symbol limit set: {symbol} = {max_position_value}")
    
    def halt_trading(self, reason: str):
        """Manually halt trading"""
        self._halt_trading(reason)
    
    def resume_trading(self):
        """Resume trading after halt"""
        with self._lock:
            self._trading_halted = False
            self._halt_reason = None
            logger.info("Trading resumed")
    
    def is_trading_halted(self) -> tuple[bool, Optional[str]]:
        """Check if trading is halted"""
        with self._lock:
            return self._trading_halted, self._halt_reason
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily risk statistics"""
        with self._lock:
            self._check_daily_reset()
            
            return {
                'daily_pnl': float(self._daily_loss),
                'daily_trades': self._daily_trades,
                'max_daily_loss': float(self.max_daily_loss),
                'remaining_daily_loss': float(self.max_daily_loss - abs(self._daily_loss)),
                'trading_halted': self._trading_halted,
                'halt_reason': self._halt_reason,
                'date': self._last_reset_date.isoformat()
            }
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk configuration"""
        return {
            'max_position_size': float(self.max_position_size),
            'max_daily_loss': float(self.max_daily_loss),
            'max_open_positions': self.max_open_positions,
            'position_size_type': self.position_size_type,
            'risk_per_trade': float(self.risk_per_trade),
            'emergency_stop_loss': float(self.emergency_stop_loss),
            'max_leverage': float(self.max_leverage)
        }
    
    def _check_daily_reset(self):
        """Reset daily tracking if new day"""
        current_date = datetime.utcnow().date()
        
        if current_date > self._last_reset_date:
            logger.info(
                f"Daily reset | Previous PnL: {self._daily_loss} | "
                f"Trades: {self._daily_trades}"
            )
            
            self._daily_loss = Decimal('0')
            self._daily_trades = 0
            self._last_reset_date = current_date
            
            # Auto-resume trading on new day if halted due to daily loss
            if self._trading_halted and 'daily loss' in str(self._halt_reason).lower():
                self.resume_trading()
    
    def _validate_symbol_limits(
        self,
        symbol: str,
        order_value: Decimal
    ) -> tuple[bool, Optional[str]]:
        """Validate symbol-specific limits"""
        if symbol in self._symbol_limits:
            limit = self._symbol_limits[symbol]['max_position_value']
            if order_value > limit:
                return False, (
                    f"Order value {order_value} exceeds symbol limit {limit} for {symbol}"
                )
        
        return True, None
    
    def _halt_trading(self, reason: str):
        """Internal method to halt trading"""
        with self._lock:
            self._trading_halted = True
            self._halt_reason = reason
            logger.warning(f"TRADING HALTED: {reason}")
    
    def reset_daily_stats(self):
        """Manually reset daily statistics (for testing)"""
        with self._lock:
            self._daily_loss = Decimal('0')
            self._daily_trades = 0
            logger.info("Daily statistics manually reset")
