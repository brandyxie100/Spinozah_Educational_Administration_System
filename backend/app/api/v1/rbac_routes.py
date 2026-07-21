"""Protected demo routes that exercise RBAC role guards."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_current_access_claims, require_roles
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims

router = APIRouter(prefix="/api/v1", tags=["rbac"])


class ProtectedPingResponse(BaseModel):
    """Minimal payload proving the caller passed auth/RBAC checks."""

    status: str = Field(description="Always ok when authorized")
    role: str = Field(description="Role claim from the access JWT")
    resource: str = Field(description="Logical resource name")


@router.get("/me", response_model=ProtectedPingResponse)
async def get_me(
    claims: Annotated[AccessTokenClaims, Depends(get_current_access_claims)],
) -> ProtectedPingResponse:
    """Any authenticated role may access their own identity probe."""
    return ProtectedPingResponse(status="ok", role=claims.role, resource="me")


@router.get("/admin/ping", response_model=ProtectedPingResponse)
async def admin_ping(
    claims: Annotated[AccessTokenClaims, Depends(require_roles(Role.ADMIN))],
) -> ProtectedPingResponse:
    """Admin-only probe used by RBAC tests."""
    return ProtectedPingResponse(status="ok", role=claims.role, resource="admin")


@router.get("/staff/ping", response_model=ProtectedPingResponse)
async def staff_ping(
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK, Role.TEACHER)),
    ],
) -> ProtectedPingResponse:
    """Staff probe — parents are excluded (403)."""
    return ProtectedPingResponse(status="ok", role=claims.role, resource="staff")
