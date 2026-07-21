"""Pydantic schemas for attendance check-in API."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class AttendanceCheckInRequest(BaseModel):
    """Payload to start teacher confirmation for a scheduled lesson."""

    schedule_id: UUID
    enrolment_id: UUID | None = None


class AttendanceConfirmRequest(BaseModel):
    """Teacher confirmation outcome for a pending check-in."""

    outcome: str = Field(pattern="^(present|absent)$")


class AttendanceOut(BaseModel):
    """Public attendance representation with remaining lesson balance."""

    id: UUID
    tenant_id: UUID
    schedule_id: UUID
    student_id: UUID
    enrolment_id: UUID
    status: str
    remaining_lessons: int | None
