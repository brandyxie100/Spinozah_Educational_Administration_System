"""Pydantic schemas for user management API."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.domain.identity.roles import Role


class UserCreateRequest(BaseModel):
    """Payload to create a tenant user (admin only)."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: Role


class UserUpdateRequest(BaseModel):
    """Partial update for a tenant user (admin only)."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: Role | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserOut(BaseModel):
    """Public user representation (never includes password hash)."""

    id: UUID
    tenant_id: UUID
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool


class UserListResponse(BaseModel):
    """Paginated user list."""

    items: list[UserOut]
    page: int
    page_size: int
    total: int
