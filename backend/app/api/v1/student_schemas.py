"""Pydantic schemas for student CRUD API."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class StudentCreateRequest(BaseModel):
    """Payload to create a student."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None


class StudentUpdateRequest(BaseModel):
    """Full replace payload for PUT /students/{id}."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    is_active: bool = True


class StudentOut(BaseModel):
    """Public student representation."""

    id: UUID
    tenant_id: UUID
    full_name: str
    email: EmailStr | None
    is_active: bool


class StudentListResponse(BaseModel):
    """Paginated student list."""

    items: list[StudentOut]
    page: int
    page_size: int
    total: int
