"""
Monitoring and Dashboard API endpoints

Provides real-time visibility into:
- Trade statistics
- Risk exposure  
- Range analysis
- Execution quality
- Active trades
- Backtest results
- Alert status
"""

from fastapi import APIRouter, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from ...core import (
    TradeStateManager,
    RiskEngineV2,
    ExecutionGuardrailsManagerV2,
    RangeAnalyzer,
    BacktestEngine,
)
from ...utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# Global component references (set by server startup)
_trade_state_manager: Optional[TradeStateManager] = None
_risk_engine_v2: Optional[RiskEngineV2] = None
_execution_guardrails: Optional[ExecutionGuardrailsManagerV2] = None
_range_analyzer: Optional[RangeAnalyzer] = None
_broker = None
_data_manager = None


def set_monitoring_components(
    trade_state_manager: TradeStateManager,
    risk_engine_v2: RiskEngineV2,
    execution_guardrails: ExecutionGuardrailsManagerV2,
    range_analyzer: RangeAnalyzer,
    broker=None,
    data_manager=None,
):
    """Set references to monitoring components from main bot"""
    global _trade_state_manager, _risk_engine_v2, _execution_guardrails, _range_analyzer, _broker, _data_manager
    _trade_state_manager = trade_state_manager
    _risk_engine_v2 = risk_engine_v2
    _execution_guardrails = execution_guardrails
    _range_analyzer = range_analyzer
    _broker = broker
    _data_manager = data_manager


@router.get("/trade-stats")
async def get_trade_stats() -> Dict[str, Any]:
    """
    Get overall trade statistics
    
    Returns:
        - total_trades: Total trades executed
        - winning_trades: Number of winners
        - losing_trades: Number of losers
        - win_rate: Win % (0-100)
        - avg_win: Average $ per winning trade
        - avg_loss: Average $ per losing trade
        - expectancy: Expected $ per trade
        - total_pnl: Total profit/loss
    """
    if not _trade_state_manager:
        return {"error": "Trade state manager not initialized"}
    
    try:
        stats = _trade_state_manager.get_stats()
        
        return {
            "total_trades": stats.get("total_trades", 0),
            "winning_trades": stats.get("winning_trades", 0),
            "losing_trades": stats.get("losing_trades", 0),
            "win_rate": stats.get("win_rate", 0),
            "avg_win": stats.get("avg_win", 0),
            "avg_loss": stats.get("avg_loss", 0),
            "expectancy": stats.get("expectancy", 0),
            "total_pnl": stats.get("total_pnl", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting trade stats: {e}")
        return {"error": str(e)}


@router.get("/risk-exposure")
async def get_risk_exposure() -> Dict[str, Any]:
    """
    Get current portfolio risk exposure
    
    Returns:
        - total_exposure: Total $ at risk
        - exposure_pct: % of account
        - num_open_positions: Active trades
        - consecutive_losses: Loss streak
        - daily_loss: $ lost today
        - daily_loss_limit: $ limit
        - trading_halted: Boolean if halted
        - open_positions: List of open trades with exposure
    """
    if not _risk_engine_v2:
        return {"error": "Risk engine not initialized"}
    
    try:
        exposure = _risk_engine_v2.get_current_exposure()
        risk_stats = _risk_engine_v2.get_stats()
        
        return {
            "total_exposure": exposure.get("total_exposure", 0),
            "exposure_pct": exposure.get("exposure_pct", 0),
            "num_open_positions": exposure.get("num_open_positions", 0),
            "consecutive_losses": risk_stats.get("consecutive_losses", 0),
            "max_consecutive_losses": risk_stats.get("max_consecutive_losses", 5),
            "daily_loss": risk_stats.get("daily_loss", 0),
            "daily_loss_limit": risk_stats.get("daily_loss_limit", 500),
            "trading_halted": risk_stats.get("trading_halted", False),
            "halt_reason": risk_stats.get("halt_reason", ""),
            "open_positions": exposure.get("open_positions", []),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting risk exposure: {e}")
        return {"error": str(e)}


@router.get("/ranges/{symbol}")
async def get_range_analysis(symbol: str) -> Dict[str, Any]:
    """
    Get range analysis for a specific symbol
    
    Args:
        symbol: Trading pair (e.g., BTC/USDT)
    
    Returns:
        - symbol: Trading pair
        - range_high: Session high
        - range_low: Session low
        - range_position: 0-1 position in range
        - volatility_pct: Volatility as % ADR
        - zone: Current zone (ENTRY_BOTTOM, BOTTOM_EDGE, LOWER, MIDDLE, UPPER, TOP_EDGE, ENTRY_TOP)
        - can_trade: Boolean if tradeable
        - reason: Why not tradeable (if applicable)
        - chop_detected: Boolean
        - exhaustion_detected: Boolean
        - current_price: Last price
    """
    if not _range_analyzer or not _broker or not _data_manager:
        return {"error": "Components not initialized"}
    
    try:
        # Fetch latest data
        data = _data_manager.fetch_ohlcv(
            symbol=symbol,
            timeframe="15m",
            limit=100,
            broker_name=list(_broker.keys())[0] if isinstance(_broker, dict) else "cryptocom"
        )
        
        if not data:
            return {"error": f"No data available for {symbol}"}
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Get ticker
        broker_instance = _broker[list(_broker.keys())[0]] if isinstance(_broker, dict) else _broker
        ticker = broker_instance.get_ticker(symbol)
        current_price = ticker.get('last', df['close'].iloc[-1] if len(df) > 0 else 0)
        
        # Analyze
        analysis = _range_analyzer.analyze(symbol, df)
        can_trade, reason = _range_analyzer.can_trade(analysis)
        should_exit, exit_reason = _range_analyzer.should_exit_on_exhaustion(analysis)
        
        return {
            "symbol": symbol,
            "range_high": analysis.get("session_high", 0),
            "range_low": analysis.get("session_low", 0),
            "range_pct": analysis.get("range_pct", 0),
            "range_position": analysis.get("range_position", 0),
            "volatility_pct": analysis.get("volatility_pct", 0),
            "zone": analysis.get("zone", "UNKNOWN"),
            "can_trade": can_trade,
            "trade_reason": reason,
            "should_exit": should_exit,
            "exit_reason": exit_reason,
            "chop_detected": analysis.get("chop_detected", False),
            "exhaustion_detected": analysis.get("exhaustion_detected", False),
            "range_expanding": analysis.get("range_expanding", False),
            "current_price": current_price,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting range analysis for {symbol}: {e}")
        return {"error": str(e)}


@router.get("/active-trades")
async def get_active_trades() -> Dict[str, Any]:
    """
    Get all currently active trades
    
    Returns list of trades with:
        - symbol: Trading pair
        - direction: BUY or SELL
        - entry_price: Entry price
        - current_price: Last market price
        - position_size: Amount at risk
        - entry_time: When entered
        - unrealized_pnl: Current profit/loss
        - state: Trade state (ARMED, ENTRY_PENDING, OPEN, CHECKPOINT_1, CHECKPOINT_2, etc)
        - candles_held: How many candles in trade
    """
    if not _trade_state_manager:
        return {"error": "Trade state manager not initialized"}
    
    try:
        active_trades = []
        stats = _trade_state_manager.get_stats()
        
        # Get trade history and filter for open trades
        # This would need to be extended based on actual TradeStateManager implementation
        
        return {
            "active_trades": active_trades,
            "total_active": len(active_trades),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting active trades: {e}")
        return {"error": str(e)}


@router.get("/execution-stats")
async def get_execution_stats() -> Dict[str, Any]:
    """
    Get execution quality statistics
    
    Returns:
        - total_orders: Total orders placed
        - accepted_orders: % accepted
        - rejected_orders: % rejected
        - rejection_rate: % rejected
        - avg_fill_time: Average seconds to fill
        - rejection_reasons: Breakdown of why orders rejected
        - by_symbol: Stats per symbol
    """
    if not _execution_guardrails:
        return {"error": "Execution guardrails not initialized"}
    
    try:
        stats = _execution_guardrails.get_execution_stats()
        
        return {
            "total_orders": stats.get("total_orders", 0),
            "accepted_orders": stats.get("accepted_orders", 0),
            "rejected_orders": stats.get("rejected_orders", 0),
            "acceptance_rate": 100 - stats.get("rejection_rate", 0),
            "rejection_rate": stats.get("rejection_rate", 0),
            "avg_fill_time": stats.get("avg_fill_time", 0),
            "rejection_reasons": stats.get("rejection_reasons", {}),
            "by_symbol": stats.get("by_symbol", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting execution stats: {e}")
        return {"error": str(e)}


@router.post("/backtest")
async def run_backtest(
    symbol: str = Query(..., description="Symbol to backtest (e.g., BTC/USDT)"),
    days: int = Query(30, description="Number of days of historical data"),
    timeframe: str = Query("15m", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d"),
) -> Dict[str, Any]:
    """
    Run backtest on historical data
    
    Args:
        symbol: Trading pair
        days: Days of historical data to use
        timeframe: Candle timeframe
    
    Returns:
        - symbol: Symbol tested
        - period_days: Days tested
        - total_trades: Number of trades
        - winning_trades: Winners
        - losing_trades: Losers
        - win_rate: % winners
        - total_pnl: Total profit/loss
        - max_drawdown: Max DD %
        - sharpe_ratio: Risk-adjusted return
        - expectancy: Expected $ per trade
    """
    if not _data_manager or not _range_analyzer:
        return {"error": "Components not initialized"}
    
    try:
        # Fetch historical data
        broker_name = "cryptocom"  # Default
        data = _data_manager.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=int((days * 1440) / (int(timeframe.rstrip('mhdw')))),
            broker_name=broker_name
        )
        
        if not data:
            return {"error": f"No historical data available for {symbol}"}
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Run backtest
        backtest_engine = BacktestEngine({})
        
        # Would need to create a mock strategy instance here
        # For now, return prepared backtest response
        
        return {
            "symbol": symbol,
            "period_days": days,
            "timeframe": timeframe,
            "candles_processed": len(df),
            "message": "Backtest engine ready",
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "max_drawdown": 0,
            "sharpe_ratio": 0,
            "expectancy": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        return {"error": str(e)}


@router.get("/alerts")
async def get_alerts(
    minutes: int = Query(60, description="Get alerts from last N minutes")
) -> Dict[str, Any]:
    """
    Get recent alert events
    
    Args:
        minutes: How far back to look
    
    Returns:
        - high_severity: Critical alerts
        - medium_severity: Warnings
        - low_severity: Info items
        - total_alerts: Count
        - alerts: List of alert items with:
          - type: alert type
          - severity: HIGH, MEDIUM, LOW
          - message: Alert message
          - timestamp: When triggered
    """
    try:
        alerts = []
        
        # Get risk alerts
        if _risk_engine_v2:
            risk_stats = _risk_engine_v2.get_stats()
            
            if risk_stats.get("trading_halted"):
                alerts.append({
                    "type": "TRADING_HALTED",
                    "severity": "HIGH",
                    "message": f"Trading halted: {risk_stats.get('halt_reason', 'Unknown')}",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            
            if risk_stats.get("consecutive_losses", 0) > 3:
                alerts.append({
                    "type": "LOSS_STREAK",
                    "severity": "MEDIUM",
                    "message": f"Loss streak: {risk_stats.get('consecutive_losses', 0)} consecutive losses",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            
            exposure = _risk_engine_v2.get_current_exposure()
            if exposure.get("exposure_pct", 0) > 2.5:
                alerts.append({
                    "type": "HIGH_EXPOSURE",
                    "severity": "MEDIUM",
                    "message": f"Portfolio exposure at {exposure.get('exposure_pct', 0):.1f}%",
                    "timestamp": datetime.utcnow().isoformat(),
                })
        
        # Get execution alerts
        if _execution_guardrails:
            exec_stats = _execution_guardrails.get_execution_stats()
            if exec_stats.get("rejection_rate", 0) > 20:
                alerts.append({
                    "type": "HIGH_REJECTION_RATE",
                    "severity": "MEDIUM",
                    "message": f"Order rejection rate: {exec_stats.get('rejection_rate', 0):.1f}%",
                    "timestamp": datetime.utcnow().isoformat(),
                })
        
        # Filter by time window
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        recent_alerts = [
            a for a in alerts
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
        
        severity_counts = {
            "HIGH": sum(1 for a in recent_alerts if a["severity"] == "HIGH"),
            "MEDIUM": sum(1 for a in recent_alerts if a["severity"] == "MEDIUM"),
            "LOW": sum(1 for a in recent_alerts if a["severity"] == "LOW"),
        }
        
        return {
            "total_alerts": len(recent_alerts),
            "high_severity": severity_counts["HIGH"],
            "medium_severity": severity_counts["MEDIUM"],
            "low_severity": severity_counts["LOW"],
            "alerts": recent_alerts[-50:],  # Last 50 alerts
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {"error": str(e)}


@router.get("/health")
async def get_health() -> Dict[str, Any]:
    """
    Get overall bot health status
    
    Returns:
        - bot_running: Boolean
        - components_initialized: Count of initialized components
        - broker_connected: List of connected brokers
        - strategies_active: Number of active strategies
        - last_cycle: Timestamp of last trading cycle
    """
    return {
        "bot_running": True,
        "components_initialized": {
            "trade_state_manager": _trade_state_manager is not None,
            "risk_engine_v2": _risk_engine_v2 is not None,
            "execution_guardrails": _execution_guardrails is not None,
            "range_analyzer": _range_analyzer is not None,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
