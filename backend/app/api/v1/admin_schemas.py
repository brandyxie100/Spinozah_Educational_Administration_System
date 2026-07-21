"""Pydantic schemas for admin KPI dashboard APIs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class RevenuePeriodOut(BaseModel):
    """One bar on the paid-revenue chart."""

    period: str
    amount: Decimal


class TodayScheduleOut(BaseModel):
    """One lesson on today's schedule overview."""

    schedule_id: UUID
    teacher_id: UUID
    student_id: UUID
    starts_at: datetime
    ends_at: datetime
    classroom: str | None


class AdminKpisOut(BaseModel):
    """Admin operational KPI payload."""

    student_count: int
    teacher_count: int
    today_schedule_count: int
    unpaid_invoice_count: int
    unpaid_invoice_total: Decimal
    revenue_final_amount_sum: Decimal
    revenue_by_period: list[RevenuePeriodOut]
    today_schedules: list[TodayScheduleOut]
