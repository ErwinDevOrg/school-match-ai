"""
API Router Registry

Combines all domain routers into a single API router with /api/v1 prefix.
"""

from fastapi import APIRouter

from src.domains.auth.router import router as auth_router
from src.domains.user.router import router as user_router

# Create main API router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")

# Include all domain routers
api_router.include_router(auth_router)
api_router.include_router(user_router)

__all__ = ["api_router"]

