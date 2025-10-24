"""
Authentication API Router

Provides authentication endpoints for user registration, login, token refresh, and logout.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.models import User
from src.domains.auth.schemas import (
    LogoutRequest,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegistration,
)
from src.domains.auth.service import AuthService
from src.domains.user.schemas import UserResponse
from src.shared.dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    data: UserRegistration,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Register a new user account
    
    - **email**: Unique email address
    - **password**: Password (minimum 8 characters)
    - **full_name**: Optional full name
    
    Returns the created user profile (without tokens in response body).
    Access and refresh tokens are provided for immediate authentication.
    """
    auth_service = AuthService(db)
    user, tokens = await auth_service.register(data)
    
    # Return user data with tokens in a separate response
    response = UserResponse.model_validate(user)
    return response


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password"
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and receive access & refresh tokens
    
    - **email**: User email address
    - **password**: User password
    
    Returns JWT access token (valid for 15 minutes) and refresh token (valid for 7 days).
    """
    auth_service = AuthService(db)
    user, tokens = await auth_service.login(data)
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token"
)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token
    
    - **refresh_token**: Valid JWT refresh token
    
    Returns new access and refresh tokens (token rotation).
    The old refresh token will be revoked.
    """
    auth_service = AuthService(db)
    new_tokens = await auth_service.refresh_token(data.refresh_token)
    return new_tokens


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and revoke tokens"
)
async def logout(
    data: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Logout user and revoke refresh token(s)
    
    - **refresh_token**: Optional. Specific token to revoke. If not provided, revokes all user tokens.
    
    Requires authentication (access token in Authorization header).
    """
    auth_service = AuthService(db)
    await auth_service.logout(current_user.id, data.refresh_token)
    return None

