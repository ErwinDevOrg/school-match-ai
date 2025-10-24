"""
User API Router

Provides user profile management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.models import User
from src.domains.user.schemas import PasswordChange, UserResponse, UserUpdate
from src.domains.user.service import UserService
from src.shared.dependencies import get_current_user, get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get the authenticated user's profile
    
    Requires authentication (access token in Authorization header).
    """
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile"
)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update the authenticated user's profile
    
    - **email**: Update email address
    - **full_name**: Update full name
    
    Requires authentication (access token in Authorization header).
    """
    user_service = UserService(db)
    updated_user = await user_service.update_profile(current_user.id, data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(updated_user)


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change user password"
)
async def change_my_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Change the authenticated user's password
    
    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)
    
    Requires authentication (access token in Authorization header).
    """
    user_service = UserService(db)
    await user_service.change_password(current_user.id, data)
    return None

