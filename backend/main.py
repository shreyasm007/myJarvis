"""
FastAPI application entry point.

Configures and runs the RAG chatbot API server.
"""

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.api.routes import router
from backend.config import get_settings
from backend.core.limiter import limiter
from backend.core.exceptions import RAGException
from backend.core.logging_config import get_logger, setup_logging
from backend.core.proxy_config import configure_proxy

# Configure proxy first (if needed)
configure_proxy()

# Initialize logging
settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting RAG Chatbot API")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"CORS origins: {settings.cors_origins_list}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Chatbot API")

# Create FastAPI application
app = FastAPI(
    title="Portfolio RAG Chatbot API",
    description="A professional RAG-powered chatbot for portfolio websites",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Add rate limiter state and handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Conversation-ID"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware for request logging.
    
    Logs request details and response time.
    """
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
        },
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        f"Response: {response.status_code} ({duration_ms:.2f}ms)",
        extra={
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    
    # Add timing header
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
    
    return response


@app.exception_handler(RAGException)
async def rag_exception_handler(request: Request, exc: RAGException):
    """Handle RAG-specific exceptions."""
    logger.error(f"RAG Exception: {exc.message}", extra=exc.details)
    
    # Sanitize response in production: hide detailed error info from client
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message if not settings.is_production else "An error occurred while processing your request",
            "detail": exc.details if not settings.is_production else None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "detail": str(exc) if not settings.is_production else None,
        },
    )


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs" if not settings.is_production else "disabled",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=not settings.is_production,
    )
