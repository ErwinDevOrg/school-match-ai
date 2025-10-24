"""
Custom Exception Classes

This module defines application-specific exceptions with consistent
error codes and HTTP status codes.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """
    Base exception class for all application exceptions
    
    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error details
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        result = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class AuthenticationError(AppException):
    """
    Exception raised for authentication failures
    
    HTTP Status: 401 Unauthorized
    """
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401,
            details=details,
        )


class AuthorizationError(AppException):
    """
    Exception raised for authorization failures
    
    HTTP Status: 403 Forbidden
    """
    
    def __init__(
        self,
        message: str = "Permission denied",
        error_code: str = "AUTHORIZATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=403,
            details=details,
        )


class ValidationError(AppException):
    """
    Exception raised for validation errors
    
    HTTP Status: 422 Unprocessable Entity
    """
    
    def __init__(
        self,
        message: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=422,
            details=details,
        )


class NotFoundError(AppException):
    """
    Exception raised when a resource is not found
    
    HTTP Status: 404 Not Found
    """
    
    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=404,
            details=details,
        )


class ConflictError(AppException):
    """
    Exception raised for conflict errors (e.g., duplicate resource)
    
    HTTP Status: 409 Conflict
    """
    
    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=409,
            details=details,
        )

