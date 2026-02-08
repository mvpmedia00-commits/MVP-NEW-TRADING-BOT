"""
DASHBOARD & MONITORING API ADDITIONS
====================================

This file shows how to add new API endpoints for the enhanced monitoring.


NEW API ENDPOINTS TO ADD (bot/api/routes/monitoring.py):
=========================================================
"""

# monitoring.py - NEW FILE

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import pandas as pd

from ...core import TradeStateManager, RiskEngineV2, RangeAnalyzer

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# Global references (set by main bot)
_trade_state_manager: TradeStateManager = None
_risk_engine: RiskEngineV2 = None
_range_analyzer: RangeAnalyzer = None


def set_components(trade_mgr, risk_eng, range_ana):
    global _trade_state_manager, _risk_engine, _range_analyzer
    _trade_state_manager = trade_mgr
    _risk_engine = risk_eng
    _range_analyzer = range_ana


@router.get("/trade-stats")
async def get_trade_stats():
    """Get current trade statistics"""
    if not _trade_state_manager:
        raise HTTPException(status_code=503, detail="Trade manager not initialized")
    
    stats = _trade_state_manager.get_stats()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "trades": {
            "total": stats['total_trades'],
            "wins": stats['winning_trades'],
            "losses": stats['losing_trades'],
            "win_rate": f"{stats['win_rate']:.1f}%",
            "expectancy": f"${stats['avg_pnl']:.2f}",
        }
    }


@router.get("/risk-exposure")
async def get_risk_exposure():
    """Get current portfolio risk exposure"""
    if not _risk_engine:
        raise HTTPException(status_code=503, detail="Risk engine not initialized")
    
    exposure = _risk_engine.get_current_exposure()
    stats = _risk_engine.get_stats()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "exposure": {
            "total_usd": f"${exposure['total_exposure']:.2f}",
            "max_allowed": f"${exposure['max_allowed']:.2f}",
            "utilization_pct": f"{(exposure['total_exposure']/exposure['max_allowed']*100):.1f}%",
            "by_asset": exposure['exposure_by_asset'],
        },
        "risk": {
            "consecutive_losses": stats['consecutive_losses'],
            "daily_loss": f"${stats['daily_loss']:.2f}",
            "balance": f"${stats['current_balance']:.2f}",
        }
    }


@router.get("/active-trades")
async def get_active_trades():
    """Get all active trades with state"""
    if not _trade_state_manager:
        raise HTTPException(status_code=503, detail="Trade manager not initialized")
    
    active_trades = []
    
    # This requires access to the internal dict
    # Adjust based on actual implementation
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "active_trades": active_trades,
        "count": len(active_trades)
    }


@router.get("/ranges/{symbol}")
async def get_range_analysis(symbol: str):
    """Get current range analysis for symbol"""
    if not _range_analyzer:
        raise HTTPException(status_code=503, detail="Range analyzer not initialized")
    
    analysis = _range_analyzer.get_cache(symbol)
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No analysis for {symbol}")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "price": f"${analysis['price']:.2f}",
        "range": {
            "high": f"${analysis['range_high']:.2f}",
            "low": f"${analysis['range_low']:.2f}",
            "position": f"{analysis['range_position']:.1%}",
            "zone": analysis['zone'],
        },
        "volatility": {
            "pct": f"{analysis['volatility_pct']:.2f}%",
            "is_chop": analysis['is_chop'],
            "is_exhaustion": analysis['is_exhaustion'],
        }
    }


@router.get("/backtest")
async def run_backtest(
    symbol: str = "BTC_USD",
    days: int = 30
):
    \"\"\"
    Run backtest on historical data
    
    Query params:
    - symbol: Trading symbol (BTC_USD, ETH_USD, etc.)
    - days: Number of days of history to backtest
    \"\"\"
    from ...core import BacktestEngine, VGCryptoStrategy
    from ...brokers import get_broker_class
    from ...utils import ConfigLoader
    
    try:
        # Load config
        config_loader = ConfigLoader()
        strategy_config = config_loader.load_strategy_config()
        broker_config = config_loader.load_broker_config('cryptocom')
        
        # Get broker
        broker_class = get_broker_class('cryptocom')
        broker = broker_class(broker_config)
        broker.connect()
        
        # Fetch historical data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        ohlcv_data = broker.get_ohlcv(symbol, timeframe='15m', limit=days*96)
        
        if not ohlcv_data:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        # Create DataFrame
        df = pd.DataFrame(
            ohlcv_data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Create strategy
        strategy_cfg = strategy_config['strategies'].get('vg_crypto_btc', {})
        strategy = VGCryptoStrategy(strategy_cfg)
        
        # Run backtest
        backtest_engine = BacktestEngine({'initial_balance': 10000})
        metrics = backtest_engine.run_backtest(strategy, df, symbol=symbol)
        
        return {
            "symbol": symbol,
            "period": f"{start_time.date()} to {end_time.date()}",
            "results": metrics.to_dict(),
            "trades": [
                {
                    "entry": f"${t['entry_price']:.2f}",
                    "exit": f"${t['exit_price']:.2f}",
                    "pnl": f"${t['pnl']:.2f}",
                    "pnl_pct": f"{t['pnl_pct']:.2f}%",
                }
                for t in metrics.trades[:20]  # Last 20 trades
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution-stats")
async def get_execution_stats():
    \"\"\"Get order execution statistics\"\"\"
    # This requires access to ExecutionGuardrailsManager
    # from main bot
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "stats": {
            # Requires implementation in main
        }
    }


# ============================================================
# INTEGRATION INTO api/server.py
# ============================================================

# In api/server.py, after creating app:

from .routes.monitoring import router as monitoring_router

app.include_router(monitoring_router)


# In lifespan startup, after initializing bot:

# Set monitoring components
from .routes import monitoring
monitoring.set_components(
    trade_mgr=bot_instance.trade_state_manager,
    risk_eng=bot_instance.risk_engine_v2,
    range_ana=bot_instance.range_analyzer,
)


# ============================================================
# FRONTEND DASHBOARD UPDATES (api/static/index.html)
# ============================================================

# Add these panels to the dashboard HTML:


<!-- TRADE STATS PANEL -->
<div class="panel" id="trade-stats">
    <h3>📈 Trade Statistics</h3>
    <div id="trade-stats-content">Loading...</div>
</div>

<!-- RISK EXPOSURE PANEL -->
<div class="panel" id="risk-exposure">
    <h3>⚠️ Risk Exposure</h3>
    <div id="risk-exposure-content">Loading...</div>
</div>

<!-- RANGE ANALYSIS PANEL -->
<div class="panel" id="range-analysis">
    <h3>📊 Market Range Analysis</h3>
    <div id="range-analysis-content">Loading...</div>
</div>

<!-- ACTIVE TRADES PANEL -->
<div class="panel" id="active-trades">
    <h3>🔄 Active Trades</h3>
    <table id="active-trades-table">
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Direction</th>
                <th>Entry</th>
                <th>Current P&L</th>
                <th>Time</th>
                <th>State</th>
            </tr>
        </thead>
        <tbody id="active-trades-body">
        </tbody>
    </table>
</div>


<!-- JavaScript to update panels -->
<script>
async function updateMonitoringPanels() {
    try {
        // Update trade stats
        const tradeStats = await fetch('/api/monitoring/trade-stats').then(r => r.json());
        document.getElementById('trade-stats-content').innerHTML = `
            <pre>${JSON.stringify(tradeStats.trades, null, 2)}</pre>
        `;
        
        // Update risk exposure
        const riskExposure = await fetch('/api/monitoring/risk-exposure').then(r => r.json());
        document.getElementById('risk-exposure-content').innerHTML = `
            <pre>${JSON.stringify(riskExposure, null, 2)}</pre>
        `;
        
        // Update range analysis for each symbol
        const symbols = ['BTC_USD', 'ETH_USD', 'XRP_USD', 'DOGE_USD'];
        let rangeHtml = '';
        for (const symbol of symbols) {
            try {
                const range = await fetch(`/api/monitoring/ranges/${symbol}`).then(r => r.json());
                rangeHtml += `
                    <div class="range-item">
                        <strong>${symbol}</strong>
                        <br/>Price: ${range.price}
                        <br/>Position: ${range.range.position}
                        <br/>Zone: ${range.range.zone}
                        <br/>Vol: ${range.volatility.pct} ${range.volatility.is_chop ? '🔴 CHOP' : ''}
                    </div>
                `;
            } catch (e) {
                // Skip if no data
            }
        }
        document.getElementById('range-analysis-content').innerHTML = rangeHtml;
        
    } catch (e) {
        console.error('Error updating monitoring panels:', e);
    }
}

// Update every 10 seconds
setInterval(updateMonitoringPanels, 10000);
updateMonitoringPanels(); // Initial update
</script>


# ============================================================
# ALERT SYSTEM
# ============================================================

# Add to bot/utils/alerts.py

class AlertManager:
    \"\"\"Manage trading alerts\"\"\"
    
    def __init__(self):
        self.alerts = []
    
    def add_alert(self, level, title, message):
        \"\"\"
        Add alert
        
        level: 'INFO', 'WARNING', 'CRITICAL'
        \"\"\"
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'title': title,
            'message': message,
        }
        self.alerts.append(alert)
        
        if level == 'CRITICAL':
            logger.error(f"🚨 CRITICAL ALERT: {title} - {message}")
        elif level == 'WARNING':
            logger.warning(f"⚠️  WARNING: {title} - {message}")
        else:
            logger.info(f"ℹ️  {title} - {message}")
    
    def get_active_alerts(self):
        \"\"\"Get alerts from last hour\"\"\"
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        return [
            a for a in self.alerts
            if datetime.fromisoformat(a['timestamp']) > one_hour_ago
        ]


# In main.py, add alert checks:

def _check_alerts(self):
    \"\"\"Check for alert conditions\"\"\"
    
    stats = self.risk_engine_v2.get_stats()
    
    # Alert on consecutive losses
    if stats['consecutive_losses'] >= 3:
        self.alert_manager.add_alert(
            'WARNING',
            'Consecutive Losses',
            f"{stats['consecutive_losses']} losses in a row"
        )
    
    # Alert on daily loss
    if stats['daily_loss'] > 500:  # Adjust threshold
        self.alert_manager.add_alert(
            'CRITICAL',
            'Daily Loss Limit',
            f"Daily loss: ${stats['daily_loss']:.2f}"
        )
    
    # Alert on high exposure
    exposure = self.risk_engine_v2.get_current_exposure()
    if exposure['total_exposure'] > exposure['max_allowed'] * 0.9:
        self.alert_manager.add_alert(
            'WARNING',
            'High Portfolio Exposure',
            f"${exposure['total_exposure']:.0f} / ${exposure['max_allowed']:.0f}"
        )


# API endpoint for alerts

@router.get("/alerts")
async def get_alerts():
    \"\"\"Get active alerts\"\"\"
    # Set by main bot
    alerts = _alert_manager.get_active_alerts() if _alert_manager else []
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "alerts": alerts,
        "count": len(alerts),
    }
"""
