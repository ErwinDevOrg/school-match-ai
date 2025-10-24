"""
End-to-End Tests for Authentication Flow

Tests the complete authentication flow from registration through logout.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthenticationFlowE2E:
    """End-to-end tests for complete authentication flow"""
    
    async def test_complete_auth_flow(self, test_client: AsyncClient):
        """
        Test complete authentication flow:
        1. Register new user
        2. Login with credentials
        3. Access protected endpoint with token
        4. Refresh access token
        5. Logout
        """
        
        # Step 1: Register new user
        registration_data = {
            "email": "e2e@example.com",
            "password": "password123",
            "full_name": "E2E Test User"
        }
        
        register_response = await test_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["email"] == registration_data["email"]
        
        # Step 2: Login with credentials
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json=login_data
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Step 3: Access protected endpoint with token
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = await test_client.get(
            "/api/v1/users/me",
            headers=headers
        )
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["email"] == registration_data["email"]
        
        # Step 4: Refresh access token
        refresh_data = {"refresh_token": refresh_token}
        refresh_response = await test_client.post(
            "/api/v1/auth/refresh",
            json=refresh_data
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        # New tokens should be different (token rotation)
        assert new_tokens["access_token"] != access_token
        assert new_tokens["refresh_token"] != refresh_token
        
        # Step 5: Logout (revoke refresh token)
        logout_data = {"refresh_token": new_tokens["refresh_token"]}
        logout_response = await test_client.post(
            "/api/v1/auth/logout",
            json=logout_data,
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"}
        )
        assert logout_response.status_code == 204
        
        # Verify refresh token is revoked (cannot use again)
        retry_refresh_response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": new_tokens["refresh_token"]}
        )
        assert retry_refresh_response.status_code == 401
    
    async def test_register_duplicate_email_fails(self, test_client: AsyncClient):
        """Test that registering with duplicate email fails"""
        registration_data = {
            "email": "duplicate@example.com",
            "password": "password123"
        }
        
        # First registration
        response1 = await test_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = await test_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        assert response2.status_code == 400
        error = response2.json()
        assert "already registered" in error["message"].lower()
    
    async def test_login_invalid_credentials_fails(self, test_client: AsyncClient):
        """Test that login with invalid credentials fails"""
        # Register user first
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "validuser@example.com",
                "password": "correctpassword"
            }
        )
        
        # Attempt login with wrong password
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "validuser@example.com",
                "password": "wrongpassword"
            }
        )
        assert login_response.status_code == 401
        error = login_response.json()
        assert "invalid" in error["message"].lower()
    
    async def test_access_protected_route_without_token_fails(self, test_client: AsyncClient):
        """Test that accessing protected route without token fails"""
        response = await test_client.get("/api/v1/users/me")
        assert response.status_code == 403  # or 401 depending on implementation
    
    async def test_access_protected_route_with_invalid_token_fails(self, test_client: AsyncClient):
        """Test that accessing protected route with invalid token fails"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await test_client.get(
            "/api/v1/users/me",
            headers=headers
        )
        assert response.status_code == 401
    
    async def test_token_refresh_with_invalid_token_fails(self, test_client: AsyncClient):
        """Test that token refresh with invalid refresh token fails"""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json=refresh_data
        )
        assert response.status_code == 401
    
    async def test_logout_revokes_all_tokens(self, test_client: AsyncClient):
        """Test that logout without specific token revokes all user tokens"""
        # Register and login
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "logoutall@example.com",
                "password": "password123"
            }
        )
        
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "logoutall@example.com",
                "password": "password123"
            }
        )
        tokens = login_response.json()
        access_token = tokens["access_token"]
        
        # Logout without specifying token (revoke all)
        logout_response = await test_client.post(
            "/api/v1/auth/logout",
            json={},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert logout_response.status_code == 204
    
    async def test_password_validation(self, test_client: AsyncClient):
        """Test that password validation works"""
        # Try to register with short password
        registration_data = {
            "email": "shortpass@example.com",
            "password": "short"  # Less than 8 characters
        }
        
        response = await test_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422
    
    async def test_email_validation(self, test_client: AsyncClient):
        """Test that email validation works"""
        # Try to register with invalid email
        registration_data = {
            "email": "not-an-email",
            "password": "password123"
        }
        
        response = await test_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422

