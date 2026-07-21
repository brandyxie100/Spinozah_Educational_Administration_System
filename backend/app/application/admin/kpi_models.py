"""Admin KPI snapshot models for the operational dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RevenuePeriodBucket:
    """Paid revenue aggregated for one billing period (e.g. semester label)."""

    period: str
    amount: Decimal


@dataclass(frozen=True, slots=True)
class TodayScheduleItem:
    """One lesson occurrence scheduled for today."""

    schedule_id: UUID
    teacher_id: UUID
    student_id: UUID
    starts_at: datetime
    ends_at: datetime
    classroom: str | None


@dataclass(frozen=True, slots=True)
class AdminKpiSnapshot:
    """Tenant-scoped KPIs for the admin dashboard."""

    student_count: int
    teacher_count: int
    today_schedule_count: int
    unpaid_invoice_count: int
    unpaid_invoice_total: Decimal
    revenue_final_amount_sum: Decimal
    revenue_by_period: list[RevenuePeriodBucket] = field(default_factory=list)
    today_schedules: list[TodayScheduleItem] = field(default_factory=list)
