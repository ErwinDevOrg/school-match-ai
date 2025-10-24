"""
Unit Tests for Authentication Service

Tests for AuthService business logic including registration, login, and token management.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.domains.auth.service import AuthService
from src.domains.auth.schemas import UserLogin, UserRegistration
from src.domains.auth.models import User, RefreshToken
from src.shared.exceptions import AuthenticationError, ValidationError


@pytest.fixture
def mock_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_session):
    """Create AuthService with mocked session"""
    return AuthService(mock_session)


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


class TestAuthServiceRegister:
    """Tests for user registration"""
    
    @pytest.mark.asyncio
    async def test_register_new_user_success(self, auth_service, mock_session):
        """Test successful user registration"""
        registration_data = UserRegistration(
            email="newuser@example.com",
            password="password123",
            full_name="New User"
        )
        
        # Mock repository methods
        auth_service.user_repo.email_exists = AsyncMock(return_value=False)
        auth_service.user_repo.create_user = AsyncMock(return_value=User(
            id=1,
            email=registration_data.email,
            hashed_password="hashed",
            full_name=registration_data.full_name,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ))
        auth_service.token_repo.create_token = AsyncMock(return_value=RefreshToken(
            id=1,
            user_id=1,
            token="refresh_token",
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
            created_at=datetime.utcnow()
        ))
        
        # Mock password hashing to avoid bcrypt initialization issues
        with patch('src.domains.auth.service.get_password_hash', return_value="hashed_password"):
            # Execute
            user, tokens = await auth_service.register(registration_data)
        
        # Assert
        assert user.email == registration_data.email
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        auth_service.user_repo.email_exists.assert_called_once_with(registration_data.email)
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(self, auth_service):
        """Test registration fails with duplicate email"""
        registration_data = UserRegistration(
            email="existing@example.com",
            password="password123"
        )
        
        # Mock email exists
        auth_service.user_repo.email_exists = AsyncMock(return_value=True)
        
        # Execute & Assert
        with pytest.raises(ValidationError) as exc_info:
            await auth_service.register(registration_data)
        
        assert "already registered" in str(exc_info.value.message).lower()


class TestAuthServiceLogin:
    """Tests for user login"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, sample_user):
        """Test successful login"""
        login_data = UserLogin(
            email="test@example.com",
            password="password123"
        )
        
        # Mock repository methods
        auth_service.user_repo.get_by_email = AsyncMock(return_value=sample_user)
        auth_service.user_repo.update_last_login = AsyncMock(return_value=sample_user)
        auth_service.token_repo.create_token = AsyncMock(return_value=RefreshToken(
            id=1,
            user_id=sample_user.id,
            token="refresh_token",
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
            created_at=datetime.utcnow()
        ))
        
        # Mock password verification
        with patch('src.domains.auth.service.verify_password', return_value=True):
            user, tokens = await auth_service.login(login_data)
        
        # Assert
        assert user.id == sample_user.id
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        auth_service.user_repo.update_last_login.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, auth_service):
        """Test login fails with invalid email"""
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="password123"
        )
        
        # Mock user not found
        auth_service.user_repo.get_by_email = AsyncMock(return_value=None)
        
        # Execute & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.login(login_data)
        
        assert "invalid" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, auth_service, sample_user):
        """Test login fails with invalid password"""
        login_data = UserLogin(
            email="test@example.com",
            password="wrongpassword"
        )
        
        # Mock repository
        auth_service.user_repo.get_by_email = AsyncMock(return_value=sample_user)
        
        # Mock password verification fails
        with patch('src.domains.auth.service.verify_password', return_value=False):
            with pytest.raises(AuthenticationError) as exc_info:
                await auth_service.login(login_data)
        
        assert "invalid" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, auth_service, sample_user):
        """Test login fails for inactive user"""
        sample_user.is_active = False
        login_data = UserLogin(
            email="test@example.com",
            password="password123"
        )
        
        # Mock repository
        auth_service.user_repo.get_by_email = AsyncMock(return_value=sample_user)
        
        # Mock password verification
        with patch('src.domains.auth.service.verify_password', return_value=True):
            with pytest.raises(AuthenticationError) as exc_info:
                await auth_service.login(login_data)
        
        assert "inactive" in str(exc_info.value.message).lower()


class TestAuthServiceTokenManagement:
    """Tests for token refresh and logout"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service, sample_user):
        """Test successful token refresh"""
        refresh_token = "valid_refresh_token"
        
        # Mock stored token
        stored_token = RefreshToken(
            id=1,
            user_id=sample_user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
            created_at=datetime.utcnow()
        )
        
        # Mock repository methods
        auth_service.token_repo.get_valid_token = AsyncMock(return_value=stored_token)
        auth_service.token_repo.revoke_token = AsyncMock(return_value=True)
        auth_service.token_repo.create_token = AsyncMock(return_value=stored_token)
        auth_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        
        # Mock JWT decode
        with patch('src.domains.auth.service.decode_token', return_value={"sub": "1"}):
            tokens = await auth_service.refresh_token(refresh_token)
        
        # Assert
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        auth_service.token_repo.revoke_token.assert_called_once_with(refresh_token)
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, auth_service):
        """Test token refresh fails with invalid token"""
        refresh_token = "invalid_token"
        
        # Mock token not found
        auth_service.token_repo.get_valid_token = AsyncMock(return_value=None)
        
        # Execute & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.refresh_token(refresh_token)
        
        assert "invalid" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_logout_specific_token(self, auth_service):
        """Test logout with specific token"""
        user_id = 1
        refresh_token = "token_to_revoke"
        
        # Mock repository
        auth_service.token_repo.revoke_token = AsyncMock(return_value=True)
        
        # Execute
        result = await auth_service.logout(user_id, refresh_token)
        
        # Assert
        assert result is True
        auth_service.token_repo.revoke_token.assert_called_once_with(refresh_token)
    
    @pytest.mark.asyncio
    async def test_logout_all_tokens(self, auth_service):
        """Test logout revokes all user tokens"""
        user_id = 1
        
        # Mock repository
        auth_service.token_repo.revoke_all_user_tokens = AsyncMock(return_value=3)
        
        # Execute
        result = await auth_service.logout(user_id, None)
        
        # Assert
        assert result is True
        auth_service.token_repo.revoke_all_user_tokens.assert_called_once_with(user_id)


class TestAuthServiceTokenGeneration:
    """Tests for JWT token generation"""
    
    @pytest.mark.asyncio
    async def test_generate_tokens_creates_both_tokens(self, auth_service, sample_user):
        """Test token generation creates access and refresh tokens"""
        # Mock repository
        auth_service.token_repo.create_token = AsyncMock(return_value=RefreshToken(
            id=1,
            user_id=sample_user.id,
            token="refresh_token",
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
            created_at=datetime.utcnow()
        ))
        
        # Execute
        tokens = await auth_service._generate_tokens(sample_user)
        
        # Assert
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        assert tokens.expires_in > 0
        auth_service.token_repo.create_token.assert_called_once()

