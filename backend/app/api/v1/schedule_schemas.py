"""Pydantic schemas for schedule create API."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduleCreateRequest(BaseModel):
    """Payload to create a lesson schedule (with optional weekly recurrence)."""

    teacher_id: UUID
    student_id: UUID
    starts_at: datetime
    ends_at: datetime
    classroom: str | None = Field(default=None, max_length=100)
    is_recurring: bool = False
    recurrence_until: date | None = None


class ScheduleConflictOut(BaseModel):
    """One conflict detail returned with HTTP 409."""

    kind: str
    existing_schedule_id: UUID
    proposed_starts_at: datetime
    proposed_ends_at: datetime
    existing_starts_at: datetime
    existing_ends_at: datetime


class ScheduleOut(BaseModel):
    """Public schedule representation."""

    id: UUID
    tenant_id: UUID
    teacher_id: UUID
    student_id: UUID
    classroom: str | None
    starts_at: datetime
    ends_at: datetime
    status: str
    is_recurring: bool
    recurrence_weekday: int | None
    recurrence_until: date | None
