"""
Integration Tests for Authentication Repositories

Tests for UserRepository and RefreshTokenRepository with actual database operations.
"""

import pytest
from datetime import datetime, timedelta

from src.domains.auth.repository import RefreshTokenRepository, UserRepository
from src.domains.auth.models import RefreshToken, User


@pytest.mark.asyncio
class TestUserRepositoryIntegration:
    """Integration tests for UserRepository"""
    
    async def test_create_user(self, test_db_session):
        """Test creating a user in database"""
        repo = UserRepository(test_db_session)
        
        # Execute
        user = await repo.create_user(
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        
        # Assert
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
    
    async def test_get_by_email(self, test_db_session):
        """Test retrieving user by email"""
        repo = UserRepository(test_db_session)
        
        # Create user
        created_user = await repo.create_user(
            email="find@example.com",
            hashed_password="hashed"
        )
        
        # Execute
        found_user = await repo.get_by_email("find@example.com")
        
        # Assert
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "find@example.com"
    
    async def test_get_by_email_not_found(self, test_db_session):
        """Test retrieving non-existent user returns None"""
        repo = UserRepository(test_db_session)
        
        # Execute
        user = await repo.get_by_email("nonexistent@example.com")
        
        # Assert
        assert user is None
    
    async def test_get_by_id(self, test_db_session):
        """Test retrieving user by ID"""
        repo = UserRepository(test_db_session)
        
        # Create user
        created_user = await repo.create_user(
            email="getbyid@example.com",
            hashed_password="hashed"
        )
        
        # Execute
        found_user = await repo.get_by_id(created_user.id)
        
        # Assert
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "getbyid@example.com"
    
    async def test_email_exists_true(self, test_db_session):
        """Test email_exists returns True for existing email"""
        repo = UserRepository(test_db_session)
        
        # Create user
        await repo.create_user(
            email="exists@example.com",
            hashed_password="hashed"
        )
        
        # Execute
        exists = await repo.email_exists("exists@example.com")
        
        # Assert
        assert exists is True
    
    async def test_email_exists_false(self, test_db_session):
        """Test email_exists returns False for non-existent email"""
        repo = UserRepository(test_db_session)
        
        # Execute
        exists = await repo.email_exists("notexists@example.com")
        
        # Assert
        assert exists is False
    
    async def test_update_last_login(self, test_db_session):
        """Test updating user's last login timestamp"""
        repo = UserRepository(test_db_session)
        
        # Create user
        user = await repo.create_user(
            email="login@example.com",
            hashed_password="hashed"
        )
        original_login = user.last_login_at
        
        # Execute
        updated_user = await repo.update_last_login(user.id)
        
        # Assert
        assert updated_user is not None
        assert updated_user.last_login_at is not None
        assert updated_user.last_login_at != original_login
    
    async def test_update_user(self, test_db_session):
        """Test updating user attributes"""
        repo = UserRepository(test_db_session)
        
        # Create user
        user = await repo.create_user(
            email="update@example.com",
            hashed_password="hashed",
            full_name="Original Name"
        )
        
        # Execute
        updated_user = await repo.update(user.id, {"full_name": "Updated Name"})
        
        # Assert
        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "update@example.com"


@pytest.mark.asyncio
class TestRefreshTokenRepositoryIntegration:
    """Integration tests for RefreshTokenRepository"""
    
    async def test_create_token(self, test_db_session):
        """Test creating a refresh token"""
        user_repo = UserRepository(test_db_session)
        token_repo = RefreshTokenRepository(test_db_session)
        
        # Create user first
        user = await user_repo.create_user(
            email="tokenuser@example.com",
            hashed_password="hashed"
        )
        
        # Execute
        expires_at = datetime.utcnow() + timedelta(days=7)
        token = await token_repo.create_token(
            user_id=user.id,
            token="test_refresh_token",
            expires_at=expires_at
        )
        
        # Assert
        assert token.id is not None
        assert token.user_id == user.id
        assert token.token == "test_refresh_token"
        assert token.revoked is False
        assert token.expires_at == expires_at
    
    async def test_get_valid_token(self, test_db_session):
        """Test retrieving a valid (non-revoked, non-expired) token"""
        user_repo = UserRepository(test_db_session)
        token_repo = RefreshTokenRepository(test_db_session)
        
        # Create user
        user = await user_repo.create_user(
            email="validtoken@example.com",
            hashed_password="hashed"
        )
        
        # Create token
        expires_at = datetime.utcnow() + timedelta(days=7)
        await token_repo.create_token(
            user_id=user.id,
            token="valid_token",
            expires_at=expires_at
        )
        
        # Execute
        found_token = await token_repo.get_valid_token("valid_token")
        
        # Assert
        assert found_token is not None
        assert found_token.token == "valid_token"
        assert found_token.revoked is False
    
    async def test_get_valid_token_revoked_returns_none(self, test_db_session):
        """Test retrieving revoked token returns None"""
        user_repo = UserRepository(test_db_session)
        token_repo = RefreshTokenRepository(test_db_session)
        
        # Create user
        user = await user_repo.create_user(
            email="revokeduser@example.com",
            hashed_password="hashed"
        )
        
        # Create and revoke token
        expires_at = datetime.utcnow() + timedelta(days=7)
        await token_repo.create_token(
            user_id=user.id,
            token="revoked_token",
            expires_at=expires_at
        )
        await token_repo.revoke_token("revoked_token")
        
        # Execute
        found_token = await token_repo.get_valid_token("revoked_token")
        
        # Assert
        assert found_token is None
    
    async def test_get_valid_token_expired_returns_none(self, test_db_session):
        """Test retrieving expired token returns None"""
        user_repo = UserRepository(test_db_session)
        token_repo = RefreshTokenRepository(test_db_session)
        
        # Create user
        user = await user_repo.create_user(
            email="expireduser@example.com",
            hashed_password="hashed"
        )
        
        # Create expired token
        expires_at = datetime.utcnow() - timedelta(days=1)  # Expired
        await token_repo.create_token(
            user_id=user.id,
            token="expired_token",
            expires_at=expires_at
        )
        
        # Execute
        found_token = await token_repo.get_valid_token("expired_token")
        
        # Assert
        assert found_token is None
    
    async def test_revoke_token(self, test_db_session):
        """Test revoking a refresh token"""
        user_repo = UserRepository(test_db_session)
        token_repo = RefreshTokenRepository(test_db_session)
        
        # Create user and token
        user = await user_repo.create_user(
            email="revoketest@example.com",
            hashed_password="hashed"
        )
        expires_at = datetime.utcnow() + timedelta(days=7)
        await token_repo.create_token(
            user_id=user.id,
            token="token_to_revoke",
            expires_at=expires_at
        )
        
        # Execute
        result = await token_repo.revoke_token("token_to_revoke")
        
        # Assert
        assert result is True
        # Verify token is revoked
        found_token = await token_repo.get_valid_token("token_to_revoke")
        assert found_token is None
    
    async def test_revoke_all_user_tokens(self, test_db_session):
        """Test revoking all tokens for a user"""
        user_repo = UserRepository(test_db_session)
        token_repo = RefreshTokenRepository(test_db_session)
        
        # Create user
        user = await user_repo.create_user(
            email="multitoken@example.com",
            hashed_password="hashed"
        )
        
        # Create multiple tokens
        expires_at = datetime.utcnow() + timedelta(days=7)
        await token_repo.create_token(user.id, "token1", expires_at)
        await token_repo.create_token(user.id, "token2", expires_at)
        await token_repo.create_token(user.id, "token3", expires_at)
        
        # Execute
        count = await token_repo.revoke_all_user_tokens(user.id)
        
        # Assert
        assert count == 3
        # Verify all tokens are revoked
        assert await token_repo.get_valid_token("token1") is None
        assert await token_repo.get_valid_token("token2") is None
        assert await token_repo.get_valid_token("token3") is None

