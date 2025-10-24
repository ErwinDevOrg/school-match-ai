"""
FastAPI Dependencies

This module provides reusable dependencies for dependency injection in routes.
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.shared.exceptions import AuthenticationError
from src.shared.security import decode_token, verify_token_type

# OAuth2 scheme for JWT bearer tokens
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions
    
    Yields:
        AsyncSession: Database session
        
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Dependency for getting current authenticated user ID from JWT token
    
    Args:
        credentials: HTTP authorization credentials with bearer token
        
    Returns:
        int: User ID from token
        
    Raises:
        HTTPException: If token is invalid or expired
        
    Usage:
        @router.get("/me")
        async def get_me(user_id: int = Depends(get_current_user_id)):
            ...
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Verify it's an access token
        if not verify_token_type(payload, "access"):
            raise AuthenticationError("Invalid token type")
        
        # Extract user ID
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
        
        return int(user_id)
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency for getting the full current user object
    
    Args:
        user_id: Current user ID from token
        db: Database session
        
    Returns:
        User: Current user object from database
        
    Usage:
        @router.get("/profile")
        async def get_profile(current_user = Depends(get_current_user)):
            ...
    """
    from src.domains.auth.models import User
    from src.domains.auth.repository import UserRepository
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user


async def get_optional_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[int]:
    """
    Dependency for getting current user ID, but returns None if not authenticated
    
    Useful for endpoints that work with or without authentication
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Optional[int]: User ID if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user_id(credentials)
    except HTTPException:
        return None

