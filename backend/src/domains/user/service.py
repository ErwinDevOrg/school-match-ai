"""
User Service

Business logic for user profile management operations.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.models import User
from src.domains.auth.repository import UserRepository
from src.domains.user.schemas import PasswordChange, UserUpdate
from src.shared.exceptions import AuthenticationError, ValidationError
from src.shared.logger import get_logger
from src.shared.security import get_password_hash, verify_password

logger = get_logger(__name__)


class UserService:
    """
    User service for profile management operations
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User instance or None if not found
        """
        logger.debug(f"Fetching user", extra={"user_id": user_id})
        
        user = await self.user_repo.get_by_id(user_id)
        
        if user:
            logger.debug(
                f"User found",
                extra={"user_id": user_id, "email": user.email}
            )
        else:
            logger.warning(f"User not found", extra={"user_id": user_id})
        
        return user
    
    async def update_profile(
        self, 
        user_id: int, 
        data: UserUpdate
    ) -> Optional[User]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            data: User update data
            
        Returns:
            Updated user instance or None if not found
            
        Raises:
            ValidationError: If email already exists
        """
        logger.info(
            f"Profile update attempt",
            extra={"user_id": user_id}
        )
        
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            logger.warning(
                f"Profile update failed: user not found",
                extra={"user_id": user_id}
            )
            return None
        
        # Check if email is being changed and already exists
        if data.email and data.email != user.email:
            if await self.user_repo.email_exists(data.email):
                logger.warning(
                    f"Profile update failed: email already in use",
                    extra={"user_id": user_id, "new_email": data.email}
                )
                raise ValidationError(
                    message="Email already in use",
                    details={"field": "email"}
                )
        
        # Update user attributes
        update_data = {}
        if data.email is not None:
            update_data["email"] = data.email
        if data.full_name is not None:
            update_data["full_name"] = data.full_name
        
        if update_data:
            updated_user = await self.user_repo.update(user_id, update_data)
            logger.info(
                f"Profile updated successfully",
                extra={
                    "user_id": user_id,
                    "updated_fields": list(update_data.keys()),
                }
            )
            return updated_user
        
        logger.debug(
            f"Profile update: no changes made",
            extra={"user_id": user_id}
        )
        return user
    
    async def change_password(
        self, 
        user_id: int, 
        data: PasswordChange
    ) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            data: Password change data
            
        Returns:
            True if successful
            
        Raises:
            AuthenticationError: If current password is incorrect
        """
        logger.info(
            f"Password change attempt",
            extra={"user_id": user_id}
        )
        
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            logger.warning(
                f"Password change failed: user not found",
                extra={"user_id": user_id}
            )
            raise AuthenticationError(message="User not found")
        
        # Verify current password
        if not verify_password(data.current_password, user.hashed_password):
            logger.warning(
                f"Password change failed: incorrect current password",
                extra={"user_id": user_id}
            )
            raise AuthenticationError(message="Current password is incorrect")
        
        # Hash and update new password
        new_hashed_password = get_password_hash(data.new_password)
        await self.user_repo.update(
            user_id, 
            {"hashed_password": new_hashed_password}
        )
        
        logger.info(
            f"Password changed successfully",
            extra={"user_id": user_id}
        )
        
        return True

