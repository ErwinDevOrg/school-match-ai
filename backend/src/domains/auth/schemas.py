"""
Authentication Domain Schemas

Pydantic models for authentication request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegistration(BaseModel):
    """
    Schema for user registration request
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., 
        min_length=8, 
        description="Password (minimum 8 characters)"
    )
    full_name: Optional[str] = Field(
        None, 
        max_length=255, 
        description="User full name"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "full_name": "John Doe"
            }
        }
    }


class UserLogin(BaseModel):
    """
    Schema for user login request
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    }


class TokenResponse(BaseModel):
    """
    Schema for authentication token response
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class TokenRefresh(BaseModel):
    """
    Schema for token refresh request
    """
    refresh_token: str = Field(..., description="JWT refresh token")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class TokenData(BaseModel):
    """
    Schema for decoded token data
    """
    user_id: int
    email: str
    exp: datetime
    
    
class LogoutRequest(BaseModel):
    """
    Schema for logout request (revokes refresh token)
    """
    refresh_token: Optional[str] = Field(
        None, 
        description="Refresh token to revoke (optional, revokes all if not provided)"
    )

