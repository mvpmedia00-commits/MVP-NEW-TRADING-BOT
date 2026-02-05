"""
Main FastAPI application server for the trading bot.
Provides RESTful API endpoints with authentication, error handling, and monitoring.
"""

import os
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.models.schemas import ErrorResponse, HealthCheck
from api.routes import portfolio, trades, strategies, control

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Load API key from environment
VALID_API_KEY = os.getenv("API_KEY", "your-secret-api-key-change-this")

# Warn if using default API key
if VALID_API_KEY == "your-secret-api-key-change-this":
    logger.warning(
        "Using default API key! Set the API_KEY environment variable for production use."
    )


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from request header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if api_key != VALID_API_KEY:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Trading Bot API server...")
    logger.info(f"API Version: {app.version}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trading Bot API server...")


# Create FastAPI application
app = FastAPI(
    title="Trading Bot API",
    description="RESTful API for managing and monitoring the trading bot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.3f}s"
    )
    
    return response


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "code": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request parameters",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthCheck,
    tags=["Health"],
    summary="Health check",
    description="Check the health status of the API and its services"
)
async def health_check():
    """
    Health check endpoint.
    Returns the current status of the API and connected services.
    """
    return HealthCheck(
        status="healthy",
        version=app.version,
        timestamp=datetime.utcnow(),
        services={
            "api": "healthy",
            "database": "healthy",  # TODO: Implement actual health checks
            "broker": "healthy",
            "bot": "running"
        }
    )


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API root",
    description="Get API information"
)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Trading Bot API",
        "version": app.version,
        "description": "RESTful API for managing and monitoring the trading bot",
        "documentation": "/docs",
        "health": "/health"
    }


# Include routers with API key authentication
app.include_router(
    portfolio.router,
    prefix="/api/v1",
    tags=["Portfolio"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    trades.router,
    prefix="/api/v1",
    tags=["Trades"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    strategies.router,
    prefix="/api/v1",
    tags=["Strategies"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    control.router,
    prefix="/api/v1",
    tags=["Control"],
    dependencies=[Depends(verify_api_key)]
)


if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
