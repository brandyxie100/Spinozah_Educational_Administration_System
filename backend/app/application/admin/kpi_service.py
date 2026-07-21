"""Application service that assembles admin KPI dashboard reads."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from app.application.admin.kpi_models import (
    AdminKpiSnapshot,
    RevenuePeriodBucket,
    TodayScheduleItem,
)
from app.domain.finance.entities import Invoice, PaymentStatus
from app.domain.scheduling.entities import ScheduleStatus
from app.infrastructure.persistence.invoice_models import PaymentStatusDB
from app.infrastructure.persistence.invoice_repository import (
    SqlAlchemyInvoiceRepository,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)
from app.infrastructure.persistence.teacher_repository import (
    SqlAlchemyTeacherRepository,
)


class AdminKpiService:
    """Aggregate student/teacher counts, revenue, and today's schedule."""

    def __init__(
        self,
        *,
        tenant_id: UUID,
        student_repository: SqlAlchemyStudentRepository,
        teacher_repository: SqlAlchemyTeacherRepository,
        schedule_repository: SqlAlchemyScheduleRepository,
        invoice_repository: SqlAlchemyInvoiceRepository,
    ) -> None:
        """Bind tenant-scoped repositories for KPI assembly."""
        _ = tenant_id
        self._students = student_repository
        self._teachers = teacher_repository
        self._schedules = schedule_repository
        self._invoices = invoice_repository

    async def get_kpis(self, *, on_date: date | None = None) -> AdminKpiSnapshot:
        """Build the admin KPI snapshot for ``on_date`` (defaults to today UTC)."""
        today = on_date or datetime.now(UTC).date()
        student_count = await self._students.count_all()
        teacher_count = await self._teachers.count_all()
        unpaid_count = await self._invoices.count_by_status(PaymentStatusDB.UNPAID)
        unpaid_total = await self._invoices.sum_final_amount_by_status(
            PaymentStatusDB.UNPAID,
        )
        revenue_sum = await self._invoices.sum_final_amount_by_status(
            PaymentStatusDB.PAID,
        )
        invoices = await self._invoices.list_all()
        today_schedules = await self._today_schedule_items(today)
        return AdminKpiSnapshot(
            student_count=student_count,
            teacher_count=teacher_count,
            today_schedule_count=len(today_schedules),
            unpaid_invoice_count=unpaid_count,
            unpaid_invoice_total=unpaid_total,
            revenue_final_amount_sum=revenue_sum,
            revenue_by_period=self._revenue_by_period(invoices),
            today_schedules=today_schedules,
        )

    @staticmethod
    def _revenue_by_period(invoices: list[Invoice]) -> list[RevenuePeriodBucket]:
        """Bucket paid invoice amounts by semester label for the revenue chart."""
        buckets: dict[str, Decimal] = {}
        for invoice in invoices:
            if invoice.status != PaymentStatus.PAID:
                continue
            key = invoice.semester_label
            buckets[key] = buckets.get(key, Decimal("0.00")) + invoice.final_amount
        return [
            RevenuePeriodBucket(period=period, amount=buckets[period])
            for period in sorted(buckets.keys())
        ]

    async def _today_schedule_items(self, today: date) -> list[TodayScheduleItem]:
        """Expand tenant schedules into concrete lessons occurring on ``today``."""
        items: list[TodayScheduleItem] = []
        for schedule in await self._schedules.list_all():
            if schedule.status in {
                ScheduleStatus.CANCELLED,
                ScheduleStatus.RESCHEDULED,
            }:
                continue
            for slot in schedule.expand_occurrences(today, today):
                items.append(
                    TodayScheduleItem(
                        schedule_id=schedule.id,
                        teacher_id=schedule.teacher_id,
                        student_id=schedule.student_id,
                        starts_at=slot.starts_at,
                        ends_at=slot.ends_at,
                        classroom=schedule.classroom,
                    ),
                )
        items.sort(key=lambda row: row.starts_at)
        return items
