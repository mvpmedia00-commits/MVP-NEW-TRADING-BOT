"""
API server for trading bot monitoring and control
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from .routes import monitoring


# Global references (will be set by main bot before starting server)
_bot_instance = None


def set_bot_instance(bot):
    """Set reference to bot instance for API access"""
    global _bot_instance
    _bot_instance = bot
    
    # Initialize monitoring components with bot references
    if hasattr(bot, 'trade_state_manager'):
        monitoring.set_monitoring_components(
            trade_state_manager=bot.trade_state_manager,
            risk_engine_v2=bot.risk_engine_v2,
            execution_guardrails=bot.execution_guardrails,
            range_analyzer=bot.range_analyzer,
            broker=bot.brokers,
            data_manager=bot.data_manager,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup and shutdown"""
    # Startup
    print("📊 API Server started - Monitoring endpoints available")
    yield
    # Shutdown
    print("📊 API Server shutdown")


# Create FastAPI app
app = FastAPI(
    title="VG Crypto Trading Bot API",
    description="Real-time monitoring and control API",
    version="1.0.0",
    lifespan=lifespan
)

# Include monitoring routes
app.include_router(monitoring.router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')


@app.get("/")
async def root():
    """Root endpoint - serve dashboard"""
    dashboard_path = os.path.join(static_dir, 'dashboard.html')
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "Welcome to VG Crypto Trading Bot API"}


@app.get("/api/health")
async def health():
    """Simple health check"""
    return {
        "status": "ok",
        "service": "VG Crypto Trading Bot API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
