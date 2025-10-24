"""
Unit Tests for User Service

Tests for UserService business logic including profile management and password changes.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.domains.user.service import UserService
from src.domains.user.schemas import PasswordChange, UserUpdate
from src.domains.auth.models import User
from src.shared.exceptions import AuthenticationError, ValidationError


@pytest.fixture
def mock_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def user_service(mock_session):
    """Create UserService with mocked session"""
    return UserService(mock_session)


@pytest.fixture
def sample_user():
    """Create sample user for testing"""
    return User(
        id=1,
        email="test@example.com",
        hashed_password="$2b$12$hashed_password",
        full_name="Test User",
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestUserServiceGetUser:
    """Tests for getting user profile"""
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, sample_user):
        """Test successfully getting user by ID"""
        user_id = 1
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        
        # Execute
        user = await user_service.get_user(user_id)
        
        # Assert
        assert user is not None
        assert user.id == user_id
        assert user.email == sample_user.email
        user_service.user_repo.get_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service):
        """Test getting non-existent user returns None"""
        user_id = 999
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=None)
        
        # Execute
        user = await user_service.get_user(user_id)
        
        # Assert
        assert user is None


class TestUserServiceUpdateProfile:
    """Tests for updating user profile"""
    
    @pytest.mark.asyncio
    async def test_update_profile_email_success(self, user_service, sample_user):
        """Test successfully updating email"""
        user_id = 1
        update_data = UserUpdate(email="newemail@example.com")
        
        updated_user = User(
            id=user_id,
            email=update_data.email,
            hashed_password=sample_user.hashed_password,
            full_name=sample_user.full_name,
            is_active=True,
            is_verified=False,
            created_at=sample_user.created_at,
            updated_at=datetime.utcnow()
        )
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repo.email_exists = AsyncMock(return_value=False)
        user_service.user_repo.update = AsyncMock(return_value=updated_user)
        
        # Execute
        result = await user_service.update_profile(user_id, update_data)
        
        # Assert
        assert result is not None
        assert result.email == update_data.email
        user_service.user_repo.email_exists.assert_called_once_with(update_data.email)
    
    @pytest.mark.asyncio
    async def test_update_profile_full_name_success(self, user_service, sample_user):
        """Test successfully updating full name"""
        user_id = 1
        update_data = UserUpdate(full_name="Updated Name")
        
        updated_user = User(
            id=user_id,
            email=sample_user.email,
            hashed_password=sample_user.hashed_password,
            full_name=update_data.full_name,
            is_active=True,
            is_verified=False,
            created_at=sample_user.created_at,
            updated_at=datetime.utcnow()
        )
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=updated_user)
        
        # Execute
        result = await user_service.update_profile(user_id, update_data)
        
        # Assert
        assert result is not None
        assert result.full_name == update_data.full_name
    
    @pytest.mark.asyncio
    async def test_update_profile_duplicate_email_fails(self, user_service, sample_user):
        """Test updating to existing email fails"""
        user_id = 1
        update_data = UserUpdate(email="existing@example.com")
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repo.email_exists = AsyncMock(return_value=True)
        
        # Execute & Assert
        with pytest.raises(ValidationError) as exc_info:
            await user_service.update_profile(user_id, update_data)
        
        assert "already in use" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_update_profile_user_not_found(self, user_service):
        """Test updating non-existent user returns None"""
        user_id = 999
        update_data = UserUpdate(full_name="New Name")
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=None)
        
        # Execute
        result = await user_service.update_profile(user_id, update_data)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_profile_same_email_allowed(self, user_service, sample_user):
        """Test updating with same email is allowed"""
        user_id = 1
        update_data = UserUpdate(email=sample_user.email)
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=sample_user)
        user_service.user_repo.email_exists = AsyncMock()  # Set up the mock
        
        # Execute
        result = await user_service.update_profile(user_id, update_data)
        
        # Assert
        assert result is not None
        # email_exists should not be called for same email
        user_service.user_repo.email_exists.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_profile_empty_data_returns_user(self, user_service, sample_user):
        """Test updating with no changes returns user"""
        user_id = 1
        update_data = UserUpdate()
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        
        # Execute
        result = await user_service.update_profile(user_id, update_data)
        
        # Assert
        assert result is not None
        assert result.id == user_id


class TestUserServiceChangePassword:
    """Tests for changing user password"""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, user_service, sample_user):
        """Test successfully changing password"""
        user_id = 1
        password_data = PasswordChange(
            current_password="oldpassword",
            new_password="newpassword123"
        )
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repo.update = AsyncMock(return_value=sample_user)
        
        # Mock password verification and hashing
        with patch('src.domains.user.service.verify_password', return_value=True):
            with patch('src.domains.user.service.get_password_hash', return_value="new_hashed"):
                result = await user_service.change_password(user_id, password_data)
        
        # Assert
        assert result is True
        user_service.user_repo.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current_password(self, user_service, sample_user):
        """Test changing password fails with wrong current password"""
        user_id = 1
        password_data = PasswordChange(
            current_password="wrongpassword",
            new_password="newpassword123"
        )
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        
        # Mock password verification fails
        with patch('src.domains.user.service.verify_password', return_value=False):
            with pytest.raises(AuthenticationError) as exc_info:
                await user_service.change_password(user_id, password_data)
        
        assert "incorrect" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, user_service):
        """Test changing password for non-existent user fails"""
        user_id = 999
        password_data = PasswordChange(
            current_password="oldpassword",
            new_password="newpassword123"
        )
        
        # Mock repository
        user_service.user_repo.get_by_id = AsyncMock(return_value=None)
        
        # Execute & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            await user_service.change_password(user_id, password_data)
        
        assert "not found" in str(exc_info.value.message).lower()

