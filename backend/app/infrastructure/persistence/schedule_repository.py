"""Tenant-scoped SQLAlchemy repository for schedules."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.scheduling.entities import Schedule
from app.infrastructure.persistence.schedule_mapper import (
    model_to_schedule,
    schedule_to_model,
)
from app.infrastructure.persistence.schedule_models import ScheduleModel
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyScheduleRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate schedules only within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create a schedule repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def list_all(self) -> list[Schedule]:
        """Return all schedules for the bound tenant as domain entities."""
        statement = self._scoped(select(ScheduleModel), ScheduleModel)
        result = await self._session.scalars(statement)
        return [model_to_schedule(row) for row in result.all()]

    async def list_by_teacher_id(self, teacher_id: UUID) -> list[Schedule]:
        """Return schedules for one teacher within the bound tenant."""
        statement = self._scoped(
            select(ScheduleModel).where(ScheduleModel.teacher_id == teacher_id),
            ScheduleModel,
        )
        result = await self._session.scalars(statement)
        return [model_to_schedule(row) for row in result.all()]

    async def add(self, schedule: Schedule) -> Schedule:
        """Persist a new schedule; enforces matching tenant_id."""
        if schedule.tenant_id != self._tenant_id:
            raise ValueError("Cannot add schedule for a different tenant")
        model = schedule_to_model(schedule)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_schedule(model)
