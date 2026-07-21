"""Pydantic schemas for attendance check-in and leave APIs."""

from __future__ import annotations

from datetime import date
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


class LeaveRequestCreate(BaseModel):
    """Payload to submit a leave request for frontdesk approval."""

    student_id: UUID
    leave_date: date
    kind: str = Field(pattern="^(sick|personal)$")
    reason: str | None = Field(default=None, max_length=500)
    enrolment_id: UUID | None = None


class LeaveRequestOut(BaseModel):
    """Public leave request representation."""

    id: UUID
    tenant_id: UUID
    student_id: UUID
    enrolment_id: UUID
    leave_date: date
    kind: str
    reason: str | None
    status: str
    is_free: bool | None
    extension_days_applied: int
