"""
Authentication Service

Business logic for user authentication operations including registration,
login, token management, and logout.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.domains.auth.models import User
from src.domains.auth.repository import RefreshTokenRepository, UserRepository
from src.domains.auth.schemas import (
    TokenResponse,
    UserLogin,
    UserRegistration,
)
from src.shared.exceptions import AuthenticationError, ValidationError
from src.shared.logger import get_logger
from src.shared.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

settings = get_settings()
logger = get_logger(__name__)


class AuthService:
    """
    Authentication service for user registration, login, and token management
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)
    
    async def register(self, data: UserRegistration) -> Tuple[User, TokenResponse]:
        """
        Register a new user and return authentication tokens
        
        Args:
            data: User registration data
            
        Returns:
            Tuple of (User instance, TokenResponse)
            
        Raises:
            ValidationError: If email already exists
        """
        logger.info(f"Registration attempt for email: {data.email}")
        
        # Check if email already exists
        if await self.user_repo.email_exists(data.email):
            logger.warning(
                f"Registration failed: email already exists",
                extra={"email": data.email}
            )
            raise ValidationError(
                message="Email already registered",
                details={"field": "email"}
            )
        
        # Hash password
        hashed_password = get_password_hash(data.password)
        
        # Create user
        user = await self.user_repo.create_user(
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name
        )
        
        logger.info(
            f"User registered successfully",
            extra={
                "user_id": user.id,
                "email": user.email,
            }
        )
        
        # Generate tokens
        tokens = await self._generate_tokens(user)
        
        return user, tokens
    
    async def login(self, data: UserLogin) -> Tuple[User, TokenResponse]:
        """
        Authenticate user and return tokens
        
        Args:
            data: User login credentials
            
        Returns:
            Tuple of (User instance, TokenResponse)
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        logger.info(f"Login attempt for email: {data.email}")
        
        # Get user by email
        user = await self.user_repo.get_by_email(data.email)
        
        if not user:
            logger.warning(
                f"Login failed: user not found",
                extra={"email": data.email}
            )
            raise AuthenticationError(message="Invalid email or password")
        
        # Verify password
        if not verify_password(data.password, user.hashed_password):
            logger.warning(
                f"Login failed: invalid password",
                extra={"user_id": user.id, "email": data.email}
            )
            raise AuthenticationError(message="Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(
                f"Login failed: account inactive",
                extra={"user_id": user.id, "email": data.email}
            )
            raise AuthenticationError(message="Account is inactive")
        
        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        logger.info(
            f"User logged in successfully",
            extra={
                "user_id": user.id,
                "email": user.email,
            }
        )
        
        # Generate tokens
        tokens = await self._generate_tokens(user)
        
        return user, tokens
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using valid refresh token (with token rotation)
        
        Args:
            refresh_token: Current refresh token
            
        Returns:
            New TokenResponse with rotated tokens
            
        Raises:
            AuthenticationError: If refresh token is invalid or expired
        """
        logger.info("Token refresh attempt")
        
        # Verify refresh token exists and is valid
        stored_token = await self.token_repo.get_valid_token(refresh_token)
        
        if not stored_token:
            logger.warning("Token refresh failed: invalid or expired token")
            raise AuthenticationError(message="Invalid or expired refresh token")
        
        # Decode token to get user info
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            
            if not user_id:
                logger.warning("Token refresh failed: invalid token payload")
                raise AuthenticationError(message="Invalid token payload")
            
            # Get user
            user = await self.user_repo.get_by_id(int(user_id))
            
            if not user or not user.is_active:
                logger.warning(
                    f"Token refresh failed: user not found or inactive",
                    extra={"user_id": user_id}
                )
                raise AuthenticationError(message="User not found or inactive")
            
            # Revoke old refresh token (token rotation)
            await self.token_repo.revoke_token(refresh_token)
            
            logger.info(
                f"Token refreshed successfully",
                extra={
                    "user_id": user.id,
                    "email": user.email,
                }
            )
            
            # Generate new tokens
            new_tokens = await self._generate_tokens(user)
            
            return new_tokens
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(
                f"Token refresh failed with exception: {str(e)}",
                exc_info=True
            )
            raise AuthenticationError(
                message=f"Token validation failed: {str(e)}"
            )
    
    async def logout(
        self, 
        user_id: int, 
        refresh_token: Optional[str] = None
    ) -> bool:
        """
        Logout user by revoking refresh token(s)
        
        Args:
            user_id: User ID
            refresh_token: Specific token to revoke, or None to revoke all
            
        Returns:
            True if successful
        """
        logger.info(
            f"Logout attempt",
            extra={
                "user_id": user_id,
                "revoke_all": refresh_token is None,
            }
        )
        
        if refresh_token:
            # Revoke specific token
            result = await self.token_repo.revoke_token(refresh_token)
            logger.info(
                f"User logged out (single token revoked)",
                extra={"user_id": user_id}
            )
            return result
        else:
            # Revoke all user tokens
            await self.token_repo.revoke_all_user_tokens(user_id)
            logger.info(
                f"User logged out (all tokens revoked)",
                extra={"user_id": user_id}
            )
            return True
    
    async def _generate_tokens(self, user: User) -> TokenResponse:
        """
        Generate access and refresh tokens for user
        
        Args:
            user: User instance
            
        Returns:
            TokenResponse with access and refresh tokens
        """
        # Create access token (15 minutes by default)
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        # Create refresh token (7 days by default)
        refresh_token_expires = timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=refresh_token_expires
        )
        
        # Store refresh token in database
        expires_at = datetime.utcnow() + refresh_token_expires
        await self.token_repo.create_token(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds())
        )

