"""Pydantic schemas for staff enrolment management APIs."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.students.entities import EnrolmentStatus


class EnrolmentCreateRequest(BaseModel):
    """Payload to create a lesson package for a student."""

    student_id: UUID
    total_lessons: int = Field(ge=0)


class EnrolmentUpdateRequest(BaseModel):
    """Partial update for lesson counts and/or status."""

    total_lessons: int | None = Field(default=None, ge=0)
    completed_lessons: int | None = Field(default=None, ge=0)
    remaining_lessons: int | None = Field(default=None, ge=0)
    status: EnrolmentStatus | None = None


class EnrolmentOut(BaseModel):
    """Public enrolment representation for staff."""

    id: UUID
    tenant_id: UUID
    student_id: UUID
    total_lessons: int
    completed_lessons: int
    remaining_lessons: int
    extension_days: int
    status: str
