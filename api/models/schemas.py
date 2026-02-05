"""
Pydantic models for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class BotStatus(str, Enum):
    """Bot status enumeration."""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"


# Portfolio Models
class Position(BaseModel):
    """Individual position model."""
    symbol: str = Field(..., description="Trading symbol")
    quantity: float = Field(..., description="Position quantity")
    average_price: float = Field(..., description="Average entry price")
    current_price: float = Field(..., description="Current market price")
    market_value: float = Field(..., description="Current market value")
    unrealized_pnl: float = Field(..., description="Unrealized profit/loss")
    unrealized_pnl_percent: float = Field(..., description="Unrealized P&L percentage")
    side: OrderSide = Field(..., description="Position side (long/short)")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "quantity": 10.0,
                "average_price": 150.50,
                "current_price": 155.25,
                "market_value": 1552.50,
                "unrealized_pnl": 47.50,
                "unrealized_pnl_percent": 3.16,
                "side": "buy"
            }
        }


class PortfolioStatus(BaseModel):
    """Overall portfolio status."""
    total_equity: float = Field(..., description="Total portfolio equity")
    cash: float = Field(..., description="Available cash")
    buying_power: float = Field(..., description="Buying power")
    positions_value: float = Field(..., description="Total positions value")
    total_pnl: float = Field(..., description="Total profit/loss")
    total_pnl_percent: float = Field(..., description="Total P&L percentage")
    timestamp: datetime = Field(..., description="Status timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_equity": 105247.50,
                "cash": 45000.00,
                "buying_power": 90000.00,
                "positions_value": 60247.50,
                "total_pnl": 5247.50,
                "total_pnl_percent": 5.24,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class PortfolioPositions(BaseModel):
    """Portfolio positions response."""
    positions: List[Position] = Field(..., description="List of open positions")
    total_positions: int = Field(..., description="Total number of positions")
    timestamp: datetime = Field(..., description="Response timestamp")


class PerformanceMetrics(BaseModel):
    """Portfolio performance metrics."""
    total_return: float = Field(..., description="Total return percentage")
    daily_return: float = Field(..., description="Daily return percentage")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    win_rate: float = Field(..., description="Win rate percentage")
    total_trades: int = Field(..., description="Total number of trades")
    winning_trades: int = Field(..., description="Number of winning trades")
    losing_trades: int = Field(..., description="Number of losing trades")
    average_win: float = Field(..., description="Average winning trade")
    average_loss: float = Field(..., description="Average losing trade")
    profit_factor: Optional[float] = Field(None, description="Profit factor")
    timestamp: datetime = Field(..., description="Metrics timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_return": 5.24,
                "daily_return": 0.15,
                "sharpe_ratio": 1.85,
                "max_drawdown": -2.34,
                "win_rate": 62.5,
                "total_trades": 48,
                "winning_trades": 30,
                "losing_trades": 18,
                "average_win": 125.50,
                "average_loss": -75.25,
                "profit_factor": 1.67,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# Trade Models
class Trade(BaseModel):
    """Individual trade model."""
    trade_id: str = Field(..., description="Unique trade identifier")
    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Trade side (buy/sell)")
    quantity: float = Field(..., description="Trade quantity")
    price: float = Field(..., description="Execution price")
    status: OrderStatus = Field(..., description="Trade status")
    strategy: str = Field(..., description="Strategy name")
    timestamp: datetime = Field(..., description="Trade timestamp")
    commission: Optional[float] = Field(None, description="Commission paid")
    pnl: Optional[float] = Field(None, description="Realized P&L")

    class Config:
        json_schema_extra = {
            "example": {
                "trade_id": "trade_12345",
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10.0,
                "price": 150.50,
                "status": "filled",
                "strategy": "momentum_strategy",
                "timestamp": "2024-01-15T09:30:00Z",
                "commission": 1.50,
                "pnl": None
            }
        }


class TradeHistory(BaseModel):
    """Trade history response."""
    trades: List[Trade] = Field(..., description="List of trades")
    total_trades: int = Field(..., description="Total number of trades")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total number of pages")


class ActiveTrades(BaseModel):
    """Active trades response."""
    trades: List[Trade] = Field(..., description="List of active trades")
    total_active: int = Field(..., description="Total number of active trades")
    timestamp: datetime = Field(..., description="Response timestamp")


# Strategy Models
class StrategyInfo(BaseModel):
    """Strategy information model."""
    strategy_id: str = Field(..., description="Unique strategy identifier")
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    enabled: bool = Field(..., description="Whether strategy is enabled")
    parameters: Dict[str, Any] = Field(..., description="Strategy parameters")
    performance: Optional[Dict[str, float]] = Field(None, description="Strategy performance metrics")

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": "momentum_1",
                "name": "Momentum Strategy",
                "description": "Trades based on price momentum indicators",
                "enabled": True,
                "parameters": {
                    "lookback_period": 20,
                    "threshold": 0.02
                },
                "performance": {
                    "total_return": 8.5,
                    "win_rate": 65.0
                }
            }
        }


class StrategyList(BaseModel):
    """List of strategies response."""
    strategies: List[StrategyInfo] = Field(..., description="List of available strategies")
    total_strategies: int = Field(..., description="Total number of strategies")
    active_strategies: int = Field(..., description="Number of active strategies")


class StrategyControl(BaseModel):
    """Strategy control request."""
    reason: Optional[str] = Field(None, description="Reason for control action")


class StrategyControlResponse(BaseModel):
    """Strategy control response."""
    strategy_id: str = Field(..., description="Strategy identifier")
    action: str = Field(..., description="Action performed")
    success: bool = Field(..., description="Whether action was successful")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(..., description="Action timestamp")


# Bot Control Models
class BotControlResponse(BaseModel):
    """Bot control response."""
    status: BotStatus = Field(..., description="Current bot status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(..., description="Action timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "running",
                "message": "Bot started successfully",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class BotStatusResponse(BaseModel):
    """Bot status response."""
    status: BotStatus = Field(..., description="Current bot status")
    uptime: Optional[int] = Field(None, description="Uptime in seconds")
    active_strategies: int = Field(..., description="Number of active strategies")
    active_positions: int = Field(..., description="Number of active positions")
    last_trade: Optional[datetime] = Field(None, description="Last trade timestamp")
    timestamp: datetime = Field(..., description="Status timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "running",
                "uptime": 3600,
                "active_strategies": 3,
                "active_positions": 5,
                "last_trade": "2024-01-15T10:25:00Z",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class EmergencyStopRequest(BaseModel):
    """Emergency stop request."""
    close_positions: bool = Field(True, description="Whether to close all positions")
    reason: str = Field(..., description="Reason for emergency stop")


class EmergencyStopResponse(BaseModel):
    """Emergency stop response."""
    success: bool = Field(..., description="Whether emergency stop was successful")
    positions_closed: int = Field(..., description="Number of positions closed")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(..., description="Action timestamp")


# Error Models
class ErrorDetail(BaseModel):
    """Error detail model."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid request parameters",
                "details": [
                    {
                        "field": "quantity",
                        "message": "Must be greater than 0",
                        "code": "value_error"
                    }
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# Health Check Models
class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Check timestamp")
    services: Dict[str, str] = Field(..., description="Service statuses")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "services": {
                    "database": "healthy",
                    "broker": "healthy",
                    "bot": "running"
                }
            }
        }
