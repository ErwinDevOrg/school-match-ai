"""
FastAPI Application Entry Point

This module initializes the FastAPI application with:
- CORS middleware configuration
- Exception handlers with structured logging
- API routers
- Health check endpoint
- Structured logging configuration
"""

import traceback

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import api_router
from src.config import get_settings
from src.shared.exceptions import AppException
from src.shared.logger import get_logger, setup_logging
from src.shared.middleware import ErrorHandlingMiddleware, LoggingMiddleware

# Setup logging first
setup_logging()

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Log application startup
logger.info(
    f"Starting {settings.PROJECT_NAME} v{settings.VERSION}",
    extra={
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters: last added = first executed)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# Include API routers
app.include_router(api_router)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions with structured logging"""
    # Get request ID if available
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log application exception
    logger.warning(
        f"Application exception: {exc.error} - {exc.message}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "error_code": exc.error,
            "status_code": exc.status_code,
            "details": exc.details,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with stack trace logging"""
    # Get request ID if available
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Get stack trace
    stack_trace = traceback.format_exc()
    
    # Log with full stack trace
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
        exc_info=True,
    )
    
    if settings.DEBUG:
        # In debug mode, return detailed error with stack trace
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "type": type(exc).__name__,
                "request_id": request_id,
                "stack_trace": stack_trace,
            },
        )
    else:
        # In production, return generic error (stack trace only in logs)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "request_id": request_id,
            },
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: API health status, timestamp, and version
    """
    from datetime import datetime
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configure uvicorn with auto-reload for development
    uvicorn_config = {
        "app": "src.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": settings.DEBUG,
        "log_level": settings.LOG_LEVEL.lower(),
    }
    
    # Add development-specific settings
    if settings.DEBUG:
        uvicorn_config.update({
            "reload": True,
            "reload_delay": 0.25,  # Fast reload for development
            "reload_dirs": ["src"],  # Watch src directory
            "log_config": None,  # Use our custom logging
        })
    
    logger.info(
        f"Starting uvicorn server on {uvicorn_config['host']}:{uvicorn_config['port']}",
        extra={
            "reload": uvicorn_config["reload"],
            "environment": settings.ENVIRONMENT,
        }
    )
    
    uvicorn.run(**uvicorn_config)

