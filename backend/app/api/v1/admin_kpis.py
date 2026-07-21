"""Admin KPI dashboard endpoints (ADMIN role only)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.admin_schemas import (
    AdminKpisOut,
    RevenuePeriodOut,
    TodayScheduleOut,
)
from app.application.admin.kpi_service import AdminKpiService
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.invoice_repository import (
    SqlAlchemyInvoiceRepository,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)
from app.infrastructure.persistence.teacher_repository import (
    SqlAlchemyTeacherRepository,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def get_admin_kpi_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[AccessTokenClaims, Depends(require_roles(Role.ADMIN))],
) -> AdminKpiService:
    """Compose admin KPI service scoped to the caller's tenant."""
    tenant_id = claims.tenant_id
    return AdminKpiService(
        tenant_id=tenant_id,
        student_repository=SqlAlchemyStudentRepository(session, tenant_id),
        teacher_repository=SqlAlchemyTeacherRepository(session, tenant_id),
        schedule_repository=SqlAlchemyScheduleRepository(session, tenant_id),
        invoice_repository=SqlAlchemyInvoiceRepository(session, tenant_id),
    )


@router.get("/kpis", response_model=AdminKpisOut)
async def get_admin_kpis(
    service: Annotated[AdminKpiService, Depends(get_admin_kpi_service)],
) -> AdminKpisOut:
    """Return student/teacher counts, revenue chart data, and today's schedule."""
    snapshot = await service.get_kpis()
    return AdminKpisOut(
        student_count=snapshot.student_count,
        teacher_count=snapshot.teacher_count,
        today_schedule_count=snapshot.today_schedule_count,
        unpaid_invoice_count=snapshot.unpaid_invoice_count,
        unpaid_invoice_total=snapshot.unpaid_invoice_total,
        revenue_final_amount_sum=snapshot.revenue_final_amount_sum,
        revenue_by_period=[
            RevenuePeriodOut(period=row.period, amount=row.amount)
            for row in snapshot.revenue_by_period
        ],
        today_schedules=[
            TodayScheduleOut(
                schedule_id=row.schedule_id,
                teacher_id=row.teacher_id,
                student_id=row.student_id,
                starts_at=row.starts_at,
                ends_at=row.ends_at,
                classroom=row.classroom,
            )
            for row in snapshot.today_schedules
        ],
    )
