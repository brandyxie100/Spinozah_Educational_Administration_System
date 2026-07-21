"""Tenant-scoped SQLAlchemy repository for students."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.student_models import StudentModel
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyStudentRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate students only within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create a student repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[StudentModel], int]:
        """Return a page of students and the total count for the tenant."""
        count_statement = self._scoped(
            select(func.count()).select_from(StudentModel),
            StudentModel,
        )
        total = int(await self._session.scalar(count_statement) or 0)
        offset = (page - 1) * page_size
        statement = (
            self._scoped(select(StudentModel), StudentModel)
            .order_by(StudentModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._session.scalars(statement)
        return list(result.all()), total

    async def get_by_id(self, student_id: UUID) -> StudentModel | None:
        """Return a student by id if it belongs to the bound tenant."""
        statement = self._scoped(
            select(StudentModel).where(StudentModel.id == student_id),
            StudentModel,
        )
        result = await self._session.scalar(statement)
        return cast(StudentModel | None, result)

    async def get_by_email(self, email: str) -> StudentModel | None:
        """Return a student by email within the bound tenant."""
        statement = self._scoped(
            select(StudentModel).where(StudentModel.email == email),
            StudentModel,
        )
        result = await self._session.scalar(statement)
        return cast(StudentModel | None, result)

    async def add(self, student: StudentModel) -> StudentModel:
        """Persist a new student; enforces matching tenant_id."""
        if student.tenant_id != self._tenant_id:
            raise ValueError("Cannot add student for a different tenant")
        self._session.add(student)
        await self._session.commit()
        await self._session.refresh(student)
        return student

    async def save(self, student: StudentModel) -> StudentModel:
        """Persist updates to an existing tenant-scoped student."""
        if student.tenant_id != self._tenant_id:
            raise ValueError("Cannot save student for a different tenant")
        await self._session.commit()
        await self._session.refresh(student)
        return student

    async def delete(self, student: StudentModel) -> None:
        """Hard-delete a tenant-scoped student row."""
        if student.tenant_id != self._tenant_id:
            raise ValueError("Cannot delete student for a different tenant")
        await self._session.delete(student)
        await self._session.commit()
