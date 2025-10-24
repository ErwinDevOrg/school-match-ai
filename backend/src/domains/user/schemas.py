"""
User Domain Schemas

Pydantic models for user profile request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """
    Schema for user profile response
    """
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(
        None, 
        description="Last login timestamp"
    )
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2025-10-24T12:00:00",
                "updated_at": "2025-10-24T12:00:00",
                "last_login_at": "2025-10-24T12:30:00"
            }
        }
    }


class UserUpdate(BaseModel):
    """
    Schema for user profile update request
    """
    full_name: Optional[str] = Field(
        None, 
        max_length=255, 
        description="User full name"
    )
    email: Optional[EmailStr] = Field(
        None, 
        description="User email address"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "John Doe Updated",
                "email": "newemail@example.com"
            }
        }
    }


class PasswordChange(BaseModel):
    """
    Schema for password change request
    """
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., 
        min_length=8, 
        description="New password (minimum 8 characters)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword456!"
            }
        }
    }

