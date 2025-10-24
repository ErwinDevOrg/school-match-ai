"""
Custom Middleware

This module provides custom middleware for logging and error handling.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.logger import get_logger

# Configure logger
logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with structured logging
    
    Logs:
    - Request method, path, and client IP
    - Response status code and processing time
    - Request ID for tracing
    - Structured extra fields for JSON logging
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Get client info
        client_host = request.client.host if request.client else "unknown"
        
        # Log request with structured data
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": client_host,
                "query_params": str(request.query_params) if request.query_params else None,
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response with structured data
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "duration": process_time,
                }
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # Log error with structured data
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {type(e).__name__}: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration": process_time,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling errors and providing consistent error responses
    
    Catches unhandled exceptions and converts them to proper HTTP responses
    with structured logging
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Get request ID if available
            request_id = getattr(request.state, "request_id", "unknown")
            
            # Log the error with structured data
            logger.exception(
                f"Unhandled exception: {type(e).__name__} in {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            # Re-raise to let FastAPI's exception handlers deal with it
            raise

