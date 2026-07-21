"""Tenant-scoped SQLAlchemy repository for teachers."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.teacher_models import TeacherModel
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyTeacherRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate teachers only within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create a teacher repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[TeacherModel], int]:
        """Return a page of teachers and the total count for the tenant."""
        count_statement = self._scoped(
            select(func.count()).select_from(TeacherModel),
            TeacherModel,
        )
        total = int(await self._session.scalar(count_statement) or 0)
        offset = (page - 1) * page_size
        statement = (
            self._scoped(select(TeacherModel), TeacherModel)
            .order_by(TeacherModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._session.scalars(statement)
        return list(result.all()), total

    async def get_by_id(self, teacher_id: UUID) -> TeacherModel | None:
        """Return a teacher by id if it belongs to the bound tenant."""
        statement = self._scoped(
            select(TeacherModel).where(TeacherModel.id == teacher_id),
            TeacherModel,
        )
        result = await self._session.scalar(statement)
        return cast(TeacherModel | None, result)

    async def get_by_email(self, email: str) -> TeacherModel | None:
        """Return a teacher by email within the bound tenant."""
        statement = self._scoped(
            select(TeacherModel).where(TeacherModel.email == email),
            TeacherModel,
        )
        result = await self._session.scalar(statement)
        return cast(TeacherModel | None, result)

    async def get_by_user_id(self, user_id: UUID) -> TeacherModel | None:
        """Return the teacher linked to ``user_id`` within the bound tenant."""
        statement = self._scoped(
            select(TeacherModel).where(TeacherModel.user_id == user_id),
            TeacherModel,
        )
        result = await self._session.scalar(statement)
        return cast(TeacherModel | None, result)

    async def add(self, teacher: TeacherModel) -> TeacherModel:
        """Persist a new teacher; enforces matching tenant_id."""
        if teacher.tenant_id != self._tenant_id:
            raise ValueError("Cannot add teacher for a different tenant")
        self._session.add(teacher)
        await self._session.commit()
        await self._session.refresh(teacher)
        return teacher

    async def save(self, teacher: TeacherModel) -> TeacherModel:
        """Persist updates to an existing tenant-scoped teacher."""
        if teacher.tenant_id != self._tenant_id:
            raise ValueError("Cannot save teacher for a different tenant")
        await self._session.commit()
        await self._session.refresh(teacher)
        return teacher

    async def delete(self, teacher: TeacherModel) -> None:
        """Hard-delete a tenant-scoped teacher row."""
        if teacher.tenant_id != self._tenant_id:
            raise ValueError("Cannot delete teacher for a different tenant")
        await self._session.delete(teacher)
        await self._session.commit()
