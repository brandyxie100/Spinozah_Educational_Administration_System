"""Tenant-scoped repositories for attendance and enrolments."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.attendance.entities import AttendanceRecord
from app.domain.students.entities import Enrolment
from app.infrastructure.persistence.attendance_mapper import (
    apply_enrolment_to_model,
    attendance_to_model,
    enrolment_to_model,
    model_to_attendance,
    model_to_enrolment,
)
from app.infrastructure.persistence.attendance_models import AttendanceModel
from app.infrastructure.persistence.student_models import (
    EnrolmentModel,
    EnrolmentStatusDB,
)
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyAttendanceRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate attendance records within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create an attendance repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def get_by_id(self, attendance_id: UUID) -> AttendanceRecord | None:
        """Return an attendance record by id for this tenant."""
        statement = self._scoped(
            select(AttendanceModel).where(AttendanceModel.id == attendance_id),
            AttendanceModel,
        )
        result = await self._session.scalar(statement)
        model = cast(AttendanceModel | None, result)
        return model_to_attendance(model) if model is not None else None

    async def get_by_schedule_id(
        self,
        schedule_id: UUID,
    ) -> AttendanceRecord | None:
        """Return attendance for a schedule if it exists in this tenant."""
        statement = self._scoped(
            select(AttendanceModel).where(AttendanceModel.schedule_id == schedule_id),
            AttendanceModel,
        )
        result = await self._session.scalar(statement)
        model = cast(AttendanceModel | None, result)
        return model_to_attendance(model) if model is not None else None

    async def list_by_student_id(self, student_id: UUID) -> list[AttendanceRecord]:
        """Return all attendance rows for a student in this tenant."""
        return await self.list(student_id=student_id)

    async def list(
        self,
        *,
        status: str | None = None,
        student_id: UUID | None = None,
        limit: int = 100,
    ) -> list[AttendanceRecord]:
        """Return attendance rows for this tenant, newest first.

        Args:
            status: Optional status filter (pending_confirmation/present/absent).
            student_id: Optional student filter.
            limit: Max rows to return (capped at 200).
        """
        capped = max(1, min(limit, 200))
        statement = select(AttendanceModel)
        if student_id is not None:
            statement = statement.where(AttendanceModel.student_id == student_id)
        if status is not None:
            statement = statement.where(AttendanceModel.status == status)
        statement = (
            self._scoped(statement, AttendanceModel)
            .order_by(AttendanceModel.created_at.desc())
            .limit(capped)
        )
        result = await self._session.scalars(statement)
        return [model_to_attendance(model) for model in result.all()]

    async def add(self, record: AttendanceRecord) -> AttendanceRecord:
        """Persist a new attendance record."""
        if record.tenant_id != self._tenant_id:
            raise ValueError("Cannot add attendance for a different tenant")
        model = attendance_to_model(record)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_attendance(model)

    async def save(self, record: AttendanceRecord) -> AttendanceRecord:
        """Persist updates to an existing attendance record."""
        if record.tenant_id != self._tenant_id:
            raise ValueError("Cannot save attendance for a different tenant")
        statement = self._scoped(
            select(AttendanceModel).where(AttendanceModel.id == record.id),
            AttendanceModel,
        )
        model = cast(AttendanceModel | None, await self._session.scalar(statement))
        if model is None:
            raise ValueError(f"Attendance not found: {record.id}")
        model.status = attendance_to_model(record).status
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_attendance(model)


class SqlAlchemyEnrolmentRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate enrolments within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create an enrolment repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def get_by_id(self, enrolment_id: UUID) -> Enrolment | None:
        """Return an enrolment by id for this tenant."""
        statement = self._scoped(
            select(EnrolmentModel).where(EnrolmentModel.id == enrolment_id),
            EnrolmentModel,
        )
        result = await self._session.scalar(statement)
        model = cast(EnrolmentModel | None, result)
        return model_to_enrolment(model) if model is not None else None

    async def get_active_for_student(self, student_id: UUID) -> Enrolment | None:
        """Return the newest active enrolment for a student, if any."""
        statement = (
            self._scoped(
                select(EnrolmentModel).where(
                    EnrolmentModel.student_id == student_id,
                    EnrolmentModel.status == EnrolmentStatusDB.ACTIVE,
                ),
                EnrolmentModel,
            )
            .order_by(EnrolmentModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.scalar(statement)
        model = cast(EnrolmentModel | None, result)
        return model_to_enrolment(model) if model is not None else None

    async def list_by_student_id(self, student_id: UUID) -> list[Enrolment]:
        """Return all enrolments for a student in this tenant (newest first)."""
        statement = (
            self._scoped(
                select(EnrolmentModel).where(EnrolmentModel.student_id == student_id),
                EnrolmentModel,
            )
            .order_by(EnrolmentModel.created_at.desc())
        )
        result = await self._session.scalars(statement)
        return [model_to_enrolment(model) for model in result.all()]

    async def list_all(self) -> list[Enrolment]:
        """Return all enrolments for this tenant (newest first)."""
        statement = self._scoped(
            select(EnrolmentModel),
            EnrolmentModel,
        ).order_by(EnrolmentModel.created_at.desc())
        result = await self._session.scalars(statement)
        return [model_to_enrolment(model) for model in result.all()]

    async def add(self, enrolment: Enrolment) -> Enrolment:
        """Insert a new enrolment for this tenant."""
        if enrolment.tenant_id != self._tenant_id:
            raise ValueError("Cannot add enrolment for a different tenant")
        model = enrolment_to_model(enrolment)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_enrolment(model)

    async def save(self, enrolment: Enrolment) -> Enrolment:
        """Persist enrolment lesson balance updates."""
        if enrolment.tenant_id != self._tenant_id:
            raise ValueError("Cannot save enrolment for a different tenant")
        statement = self._scoped(
            select(EnrolmentModel).where(EnrolmentModel.id == enrolment.id),
            EnrolmentModel,
        )
        model = cast(EnrolmentModel | None, await self._session.scalar(statement))
        if model is None:
            raise ValueError(f"Enrolment not found: {enrolment.id}")
        apply_enrolment_to_model(model, enrolment)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_enrolment(model)
