"""
End-to-End Tests for User Profile CRUD Operations

Tests user profile management including get, update, and password change.
"""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def authenticated_user(test_client: AsyncClient):
    """
    Fixture that creates and authenticates a user, returning access token and user data
    """
    # Register user
    registration_data = {
        "email": "crudtest@example.com",
        "password": "password123",
        "full_name": "CRUD Test User"
    }
    
    register_response = await test_client.post(
        "/api/v1/auth/register",
        json=registration_data
    )
    user_data = register_response.json()
    
    # Login to get tokens
    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
    )
    tokens = login_response.json()
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user_data": user_data,
        "password": registration_data["password"]
    }


@pytest.mark.asyncio
class TestUserProfileCRUDE2E:
    """End-to-end tests for user profile CRUD operations"""
    
    async def test_get_own_profile(self, test_client: AsyncClient, authenticated_user):
        """Test getting authenticated user's own profile"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        response = await test_client.get(
            "/api/v1/users/me",
            headers=headers
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == authenticated_user["user_data"]["email"]
        assert profile["full_name"] == authenticated_user["user_data"]["full_name"]
        assert "id" in profile
        assert "is_active" in profile
        assert "is_verified" in profile
        assert "created_at" in profile
        # Password should not be in response
        assert "password" not in profile
        assert "hashed_password" not in profile
    
    async def test_update_profile_full_name(self, test_client: AsyncClient, authenticated_user):
        """Test updating user's full name"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        update_data = {"full_name": "Updated Name"}
        
        response = await test_client.patch(
            "/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["full_name"] == "Updated Name"
        assert updated_profile["email"] == authenticated_user["user_data"]["email"]
    
    async def test_update_profile_email(self, test_client: AsyncClient, authenticated_user):
        """Test updating user's email"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        update_data = {"email": "newemail@example.com"}
        
        response = await test_client.patch(
            "/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["email"] == "newemail@example.com"
    
    async def test_update_profile_both_fields(self, test_client: AsyncClient, authenticated_user):
        """Test updating both email and full name"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        update_data = {
            "email": "bothupdated@example.com",
            "full_name": "Both Updated"
        }
        
        response = await test_client.patch(
            "/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["email"] == "bothupdated@example.com"
        assert updated_profile["full_name"] == "Both Updated"
    
    async def test_update_profile_duplicate_email_fails(self, test_client: AsyncClient, authenticated_user):
        """Test that updating to an existing email fails"""
        # Create another user
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "password123"
            }
        )
        
        # Try to update to existing email
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        update_data = {"email": "existing@example.com"}
        
        response = await test_client.patch(
            "/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "already in use" in error["message"].lower()
    
    async def test_update_profile_without_auth_fails(self, test_client: AsyncClient):
        """Test that updating profile without authentication fails"""
        update_data = {"full_name": "Unauthorized Update"}
        
        response = await test_client.patch(
            "/api/v1/users/me",
            json=update_data
        )
        
        assert response.status_code in [401, 403]
    
    async def test_change_password_success(self, test_client: AsyncClient, authenticated_user):
        """Test successfully changing password"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        password_data = {
            "current_password": authenticated_user["password"],
            "new_password": "newpassword456"
        }
        
        response = await test_client.put(
            "/api/v1/users/me/password",
            json=password_data,
            headers=headers
        )
        
        assert response.status_code == 204
        
        # Verify can login with new password
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": authenticated_user["user_data"]["email"],
                "password": "newpassword456"
            }
        )
        assert login_response.status_code == 200
    
    async def test_change_password_wrong_current_password(self, test_client: AsyncClient, authenticated_user):
        """Test that password change fails with wrong current password"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword456"
        }
        
        response = await test_client.put(
            "/api/v1/users/me/password",
            json=password_data,
            headers=headers
        )
        
        assert response.status_code == 401
        error = response.json()
        assert "incorrect" in error["message"].lower()
    
    async def test_change_password_validation(self, test_client: AsyncClient, authenticated_user):
        """Test password change with invalid new password"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        password_data = {
            "current_password": authenticated_user["password"],
            "new_password": "short"  # Too short
        }
        
        response = await test_client.put(
            "/api/v1/users/me/password",
            json=password_data,
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_change_password_without_auth_fails(self, test_client: AsyncClient):
        """Test that changing password without authentication fails"""
        password_data = {
            "current_password": "password123",
            "new_password": "newpassword456"
        }
        
        response = await test_client.put(
            "/api/v1/users/me/password",
            json=password_data
        )
        
        assert response.status_code in [401, 403]
    
    async def test_profile_contains_correct_fields(self, test_client: AsyncClient, authenticated_user):
        """Test that profile response contains all expected fields and no sensitive data"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        response = await test_client.get(
            "/api/v1/users/me",
            headers=headers
        )
        
        assert response.status_code == 200
        profile = response.json()
        
        # Required fields
        required_fields = ["id", "email", "is_active", "is_verified", "created_at", "updated_at"]
        for field in required_fields:
            assert field in profile, f"Missing required field: {field}"
        
        # Sensitive fields should not be present
        sensitive_fields = ["password", "hashed_password"]
        for field in sensitive_fields:
            assert field not in profile, f"Sensitive field exposed: {field}"
    
    async def test_update_profile_preserves_other_fields(self, test_client: AsyncClient, authenticated_user):
        """Test that updating one field doesn't affect other fields"""
        headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
        
        # Get original profile
        original_response = await test_client.get(
            "/api/v1/users/me",
            headers=headers
        )
        original_profile = original_response.json()
        
        # Update only full name
        update_data = {"full_name": "Only Name Changed"}
        
        response = await test_client.patch(
            "/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        
        updated_profile = response.json()
        
        # Email should remain unchanged
        assert updated_profile["email"] == original_profile["email"]
        # Other fields should remain unchanged
        assert updated_profile["is_active"] == original_profile["is_active"]
        assert updated_profile["is_verified"] == original_profile["is_verified"]

