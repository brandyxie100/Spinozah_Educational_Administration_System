"""Unit tests for AdminKpiService aggregates."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from app.application.admin.kpi_service import AdminKpiService
from app.domain.finance import Invoice, PaymentStatus
from app.domain.scheduling import Schedule, ScheduleStatus, Weekday, WeeklyRecurrence


class _CountRepo:
    def __init__(self, total: int) -> None:
        self._total = total

    async def count_all(self) -> int:
        return self._total


class _InvoiceRepo:
    def __init__(self, invoices: list[Invoice]) -> None:
        self._invoices = invoices

    async def count_by_status(self, status: object) -> int:
        value = getattr(status, "value", str(status))
        return sum(1 for inv in self._invoices if inv.status.value == value)

    async def sum_final_amount_by_status(self, status: object) -> Decimal:
        value = getattr(status, "value", str(status))
        return sum(
            (inv.final_amount for inv in self._invoices if inv.status.value == value),
            Decimal("0.00"),
        )

    async def list_all(self) -> list[Invoice]:
        return list(self._invoices)


class _ScheduleRepo:
    def __init__(self, schedules: list[Schedule]) -> None:
        self._schedules = schedules

    async def list_all(self) -> list[Schedule]:
        return list(self._schedules)


@pytest.mark.asyncio
async def test_admin_kpis_counts_revenue_and_today_schedule() -> None:
    tenant_id = uuid.uuid4()
    today = date(2026, 7, 22)  # Wednesday
    teacher_id = uuid.uuid4()
    student_id = uuid.uuid4()
    starts = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    schedule = Schedule(
        tenant_id=tenant_id,
        teacher_id=teacher_id,
        student_id=student_id,
        starts_at=starts,
        ends_at=starts + timedelta(hours=1),
        status=ScheduleStatus.NOT_STARTED,
        classroom="A1",
        recurrence=WeeklyRecurrence(weekday=Weekday.WEDNESDAY),
    )
    invoices = [
        Invoice(
            tenant_id=tenant_id,
            student_id=student_id,
            semester_label="2026-S1",
            subtotal=Decimal("100.00"),
            status=PaymentStatus.PAID,
        ),
        Invoice(
            tenant_id=tenant_id,
            student_id=student_id,
            semester_label="2026-S2",
            subtotal=Decimal("200.00"),
            credit=Decimal("20.00"),
            status=PaymentStatus.UNPAID,
        ),
    ]
    service = AdminKpiService(
        tenant_id=tenant_id,
        student_repository=_CountRepo(12),  # type: ignore[arg-type]
        teacher_repository=_CountRepo(3),  # type: ignore[arg-type]
        schedule_repository=_ScheduleRepo([schedule]),  # type: ignore[arg-type]
        invoice_repository=_InvoiceRepo(invoices),  # type: ignore[arg-type]
    )
    snapshot = await service.get_kpis(on_date=today)
    assert snapshot.student_count == 12
    assert snapshot.teacher_count == 3
    assert snapshot.today_schedule_count == 1
    assert snapshot.unpaid_invoice_count == 1
    assert snapshot.unpaid_invoice_total == Decimal("180.00")
    assert snapshot.revenue_final_amount_sum == Decimal("100.00")
    assert snapshot.revenue_by_period[0].period == "2026-S1"
    assert snapshot.today_schedules[0].classroom == "A1"
