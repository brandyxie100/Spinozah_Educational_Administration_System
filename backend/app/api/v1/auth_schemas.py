"""Auth HTTP schemas and cookie helpers."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

REFRESH_COOKIE_NAME = "refresh_token"


class LoginRequest(BaseModel):
    """Credentials for tenant-scoped login."""

    tenant_slug: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Public user fields returned with auth responses."""

    id: UUID
    tenant_id: UUID
    email: EmailStr
    full_name: str
    role: str


class TokenResponse(BaseModel):
    """Access token payload (refresh stays in httpOnly cookie)."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
