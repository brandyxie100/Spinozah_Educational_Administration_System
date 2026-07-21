"""SQLAlchemy repository for tenant-scoped user rows."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import UserModel
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyUserRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate users only within the repository's bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create a user repository scoped to ``tenant_id``.

        Args:
            session: Async SQLAlchemy session.
            tenant_id: Tenant whose users may be read/written.
        """
        super().__init__(session, tenant_id)

    async def list_users(self) -> list[UserModel]:
        """Return all users belonging to the bound tenant."""
        statement = self._scoped(select(UserModel), UserModel)
        result = await self._session.scalars(statement)
        return list(result.all())

    async def list_users_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[UserModel], int]:
        """Return a page of users and the total count for the bound tenant."""
        count_statement = self._scoped(
            select(func.count()).select_from(UserModel),
            UserModel,
        )
        total = int(await self._session.scalar(count_statement) or 0)

        offset = (page - 1) * page_size
        statement = (
            self._scoped(select(UserModel), UserModel)
            .order_by(UserModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._session.scalars(statement)
        return list(result.all()), total

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        """Return a user by id if it belongs to the bound tenant."""
        statement = self._scoped(
            select(UserModel).where(UserModel.id == user_id),
            UserModel,
        )
        result = await self._session.scalar(statement)
        return cast(UserModel | None, result)

    async def get_by_email(self, email: str) -> UserModel | None:
        """Return a user by email within the bound tenant."""
        statement = self._scoped(
            select(UserModel).where(UserModel.email == email),
            UserModel,
        )
        result = await self._session.scalar(statement)
        return cast(UserModel | None, result)

    async def add(self, user: UserModel) -> UserModel:
        """Persist a new user; enforces tenant_id matches the repository scope."""
        if user.tenant_id != self._tenant_id:
            msg = "Cannot add user for a different tenant"
            raise ValueError(msg)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def save(self, user: UserModel) -> UserModel:
        """Persist updates to an existing tenant-scoped user."""
        if user.tenant_id != self._tenant_id:
            msg = "Cannot save user for a different tenant"
            raise ValueError(msg)
        await self._session.commit()
        await self._session.refresh(user)
        return user
