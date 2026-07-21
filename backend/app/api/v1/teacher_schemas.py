"""Pydantic schemas for teacher CRUD API."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TeacherCreateRequest(BaseModel):
    """Payload to create a teacher; user_id optionally links a login account."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    user_id: UUID | None = None


class TeacherUpdateRequest(BaseModel):
    """Full replace payload for PUT /teachers/{id}."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    is_active: bool = True
    user_id: UUID | None = None


class TeacherOut(BaseModel):
    """Public teacher representation."""

    id: UUID
    tenant_id: UUID
    full_name: str
    email: EmailStr | None
    user_id: UUID | None
    is_active: bool


class TeacherListResponse(BaseModel):
    """Paginated teacher list."""

    items: list[TeacherOut]
    page: int
    page_size: int
    total: int
