"""API v1 routers."""

from app.api.v1.auth import router as auth_router
from app.api.v1.rbac_routes import router as rbac_router

__all__ = ["auth_router", "rbac_router"]
