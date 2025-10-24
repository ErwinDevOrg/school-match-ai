"""
Authentication Domain Repositories

Data access layer for User and RefreshToken models.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.models import RefreshToken, User
from src.shared.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            email: User email address
            
        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self, 
        email: str, 
        hashed_password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Create a new user
        
        Args:
            email: User email address
            hashed_password: Hashed password
            full_name: User full name (optional)
            
        Returns:
            Created user instance
        """
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update_last_login(self, user_id: int) -> Optional[User]:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.last_login_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email address to check
            
        Returns:
            True if email exists, False otherwise
        """
        result = await self.session.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Repository for RefreshToken model operations
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)
    
    async def create_token(
        self,
        user_id: int,
        token: str,
        expires_at: datetime
    ) -> RefreshToken:
        """
        Create a new refresh token
        
        Args:
            user_id: User ID
            token: Refresh token string
            expires_at: Token expiration timestamp
            
        Returns:
            Created refresh token instance
        """
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False
        )
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token
    
    async def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """
        Get a valid (non-revoked, non-expired) refresh token
        
        Args:
            token: Refresh token string
            
        Returns:
            RefreshToken instance or None if not found/invalid
        """
        now = datetime.utcnow()
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token == token,
                    RefreshToken.revoked == False,  # noqa: E712
                    RefreshToken.expires_at > now
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a refresh token
        
        Args:
            token: Refresh token string
            
        Returns:
            True if revoked, False if not found
        """
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        refresh_token = result.scalar_one_or_none()
        
        if not refresh_token:
            return False
        
        refresh_token.revoked = True
        await self.session.commit()
        return True
    
    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Revoke all refresh tokens for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of tokens revoked
        """
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False  # noqa: E712
                )
            )
        )
        tokens = result.scalars().all()
        
        for token in tokens:
            token.revoked = True
        
        await self.session.commit()
        return len(tokens)

