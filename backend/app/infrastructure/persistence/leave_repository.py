"""Tenant-scoped repository for leave requests."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.attendance.leave_policy import LeaveRequest
from app.infrastructure.persistence.leave_mapper import leave_to_model, model_to_leave
from app.infrastructure.persistence.leave_models import (
    LeaveRequestModel,
    LeaveStatusDB,
)
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyLeaveRequestRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate leave requests within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create a leave repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def get_by_id(self, leave_id: UUID) -> LeaveRequest | None:
        """Return a leave request by id for this tenant."""
        statement = self._scoped(
            select(LeaveRequestModel).where(LeaveRequestModel.id == leave_id),
            LeaveRequestModel,
        )
        result = await self._session.scalar(statement)
        model = cast(LeaveRequestModel | None, result)
        return model_to_leave(model) if model is not None else None

    async def count_approved_for_enrolment(self, enrolment_id: UUID) -> int:
        """Count approved leaves for an enrolment (term free-leave quota)."""
        statement = self._scoped(
            select(func.count()).select_from(LeaveRequestModel).where(
                LeaveRequestModel.enrolment_id == enrolment_id,
                LeaveRequestModel.status == LeaveStatusDB.APPROVED,
            ),
            LeaveRequestModel,
        )
        return int(await self._session.scalar(statement) or 0)

    async def add(self, leave: LeaveRequest) -> LeaveRequest:
        """Persist a new leave request."""
        if leave.tenant_id != self._tenant_id:
            raise ValueError("Cannot add leave for a different tenant")
        model = leave_to_model(leave)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_leave(model)

    async def save(self, leave: LeaveRequest) -> LeaveRequest:
        """Persist updates to an existing leave request."""
        if leave.tenant_id != self._tenant_id:
            raise ValueError("Cannot save leave for a different tenant")
        statement = self._scoped(
            select(LeaveRequestModel).where(LeaveRequestModel.id == leave.id),
            LeaveRequestModel,
        )
        model = cast(
            LeaveRequestModel | None,
            await self._session.scalar(statement),
        )
        if model is None:
            raise ValueError(f"Leave request not found: {leave.id}")
        updated = leave_to_model(leave)
        model.status = updated.status
        model.is_free = updated.is_free
        model.extension_days_applied = updated.extension_days_applied
        model.reason = updated.reason
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_leave(model)
