"""
Logging Configuration

This module provides structured logging configuration for development and production.
Uses JSON formatting in production for better log aggregation and plain text in development
for better readability.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from src.config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    
    Formats log records as JSON with timestamp, level, message, and context
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        
        return json.dumps(log_data)


class DevelopmentFormatter(logging.Formatter):
    """
    Custom formatter for development with colored output
    
    Formats logs in a readable format with timestamps and context
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for development"""
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        # Base format
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{color}[{record.levelname:8}]{reset} {timestamp} - {record.name} - {record.getMessage()}"
        
        # Add extra context
        extras = []
        if hasattr(record, "user_id"):
            extras.append(f"user_id={record.user_id}")
        if hasattr(record, "duration"):
            extras.append(f"duration={record.duration:.3f}s")
        if hasattr(record, "status_code"):
            extras.append(f"status={record.status_code}")
        if hasattr(record, "method") and hasattr(record, "path"):
            extras.append(f"{record.method} {record.path}")
        
        if extras:
            message += f" [{', '.join(extras)}]"
        
        # Add exception info if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        
        return message


def setup_logging() -> None:
    """
    Configure application logging based on environment
    
    - Development: Colored console output with readable format
    - Production: JSON formatted logs for log aggregation
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    # Set formatter based on environment
    if settings.ENVIRONMENT == "production":
        formatter = JSONFormatter()
    else:
        formatter = DevelopmentFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(
        f"Logging configured for {settings.ENVIRONMENT} environment "
        f"with level {settings.LOG_LEVEL}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (typically __name__ from the calling module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

