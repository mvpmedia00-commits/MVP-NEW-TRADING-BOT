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


@router.get("/api/dashboard/portfolio-history")
async def get_portfolio_history():
    """Get portfolio value history for chart"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        # Mock data for now - in production this would come from database
        portfolio = _bot_instance.portfolio.to_dict()
        current_value = portfolio.get('performance', {}).get('current_value', 10000)
        
        # Generate last 24 hours of mock data
        import random
        history = []
        base_value = current_value
        for i in range(24, 0, -1):
            timestamp = (datetime.utcnow() - timedelta(hours=i)).isoformat()
            value = base_value + random.uniform(-200, 200)
            history.append({
                "timestamp": timestamp,
                "value": round(value, 2)
            })
        
        # Add current value
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "value": round(current_value, 2)
        })
        
        return {
            "success": True,
            "data": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/pnl-history")
async def get_pnl_history():
    """Get P&L history for chart"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        portfolio = _bot_instance.portfolio.to_dict()
        current_pnl = portfolio.get('performance', {}).get('total_pnl', 0)
        
        # Mock P&L history
        import random
        history = []
        cumulative_pnl = 0
        for i in range(24, 0, -1):
            timestamp = (datetime.utcnow() - timedelta(hours=i)).isoformat()
            change = random.uniform(-50, 50)
            cumulative_pnl += change
            history.append({
                "timestamp": timestamp,
                "pnl": round(cumulative_pnl, 2)
            })
        
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "pnl": round(current_pnl, 2)
        })
        
        return {
            "success": True,
            "data": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/trade-distribution")
async def get_trade_distribution():
    """Get win/loss distribution for pie chart"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        portfolio = _bot_instance.portfolio.to_dict()
        performance = portfolio.get('performance', {})
        
        winning_trades = performance.get('winning_trades', 0)
        losing_trades = performance.get('losing_trades', 0)
        
        return {
            "success": True,
            "data": {
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "total_trades": winning_trades + losing_trades
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/dashboard/price-data")
async def get_price_data(symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 50):
    """Get candlestick price data with strategy signals"""
    if not _bot_instance:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        # Try to get data from broker
        if _bot_instance.brokers:
            broker_name = list(_bot_instance.brokers.keys())[0]
            broker = _bot_instance.brokers[broker_name]
            
            # Mock candlestick data - in production get from broker
            import random
            candles = []
            base_price = 45000 if "BTC" in symbol else 2500
            
            for i in range(limit, 0, -1):
                timestamp = (datetime.utcnow() - timedelta(hours=i)).isoformat()
                open_price = base_price + random.uniform(-500, 500)
                close_price = open_price + random.uniform(-200, 200)
                high_price = max(open_price, close_price) + random.uniform(0, 100)
                low_price = min(open_price, close_price) - random.uniform(0, 100)
                
                candles.append({
                    "timestamp": timestamp,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": round(random.uniform(100, 1000), 2),
                    "signal": random.choice([None, None, None, "BUY", "SELL"])  # Sparse signals
                })
                base_price = close_price
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "candles": candles
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="No brokers connected")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
