"""
Dashboard API endpoints for the Trading Bot
Provides real-time portfolio, trade, and market data
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

router = APIRouter(tags=["dashboard"])

# Global reference to the bot instance (set by main server)
_bot_instance = None


def set_bot_instance(bot):
    """Set the bot instance for dashboard access"""
    global _bot_instance
    _bot_instance = bot


@router.get("/api/dashboard/portfolio")
async def get_portfolio():
    """Get current portfolio status"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        portfolio = _bot_instance.portfolio.to_dict()
        return {
            "success": True,
            "data": portfolio,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/brokers")
async def get_brokers():
    """Get connected brokers and their status"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        brokers = []
        for broker_name, broker in _bot_instance.brokers.items():
            try:
                balance = broker.get_balance()
                brokers.append({
                    "name": broker_name,
                    "connected": True,
                    "balance": balance,
                    "type": getattr(broker, 'broker_type', 'unknown')
                })
            except Exception as e:
                brokers.append({
                    "name": broker_name,
                    "connected": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "data": brokers,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/strategies")
async def get_strategies():
    """Get active strategies and their status"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        strategies = []
        for strategy_name, strategy in _bot_instance.strategies.items():
            strategies.append({
                "name": strategy_name,
                "enabled": getattr(strategy, 'enabled', True),
                "parameters": getattr(strategy, 'parameters', {}),
                "description": getattr(strategy, '__doc__', 'No description')
            })
        
        return {
            "success": True,
            "data": strategies,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/market-data")
async def get_market_data(symbols: str = Query("BTC/USDT,ETH/USDT")):
    """Get current market data for symbols"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        market_data = []
        
        # Get first available broker
        broker = next(iter(_bot_instance.brokers.values()), None)
        if not broker:
            raise HTTPException(status_code=500, detail="No brokers available")
        
        for symbol in symbol_list:
            try:
                ticker = broker.get_ticker(symbol)
                market_data.append({
                    "symbol": symbol,
                    "last": ticker.get('last', 0),
                    "bid": ticker.get('bid', 0),
                    "ask": ticker.get('ask', 0),
                    "high": ticker.get('high', 0),
                    "low": ticker.get('low', 0),
                    "change": ticker.get('change', 0),
                    "changePercent": ticker.get('percentage', 0)
                })
            except Exception as e:
                market_data.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "data": market_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/positions")
async def get_positions():
    """Get current open positions"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        positions = _bot_instance.portfolio.get_all_positions()
        pos_data = []
        
        for symbol, position in positions.items():
            pos_data.append({
                "symbol": symbol,
                "type": position.position_type,
                "size": float(position.size),
                "entry_price": float(position.entry_price),
                "current_price": float(position.current_price) if position.current_price else 0,
                "pnl": float(position.get_unrealized_pnl(position.current_price or position.entry_price)) if position.current_price else 0,
                "pnl_percentage": float(position.get_pnl_percentage(position.current_price or position.entry_price)) if position.current_price else 0
            })
        
        return {
            "success": True,
            "data": pos_data,
            "count": len(pos_data),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/bot-status")
async def get_bot_status():
    """Get bot status and metrics"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        portfolio = _bot_instance.portfolio.to_dict()
        
        return {
            "success": True,
            "data": {
                "running": getattr(_bot_instance, 'running', False),
                "mode": getattr(_bot_instance, 'mode', 'unknown'),
                "initialized": True,
                "connected_brokers": len(_bot_instance.brokers),
                "active_strategies": len(_bot_instance.strategies),
                "portfolio_value": portfolio.get('performance', {}).get('current_value', 0),
                "total_pnl": portfolio.get('performance', {}).get('total_pnl', 0),
                "win_rate": portfolio.get('performance', {}).get('win_rate', 0),
                "open_positions": portfolio.get('performance', {}).get('open_positions', 0),
                "total_trades": portfolio.get('performance', {}).get('total_trades', 0)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }
