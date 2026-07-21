"""SQLAlchemy repository for tenant-scoped user rows."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import UserModel
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyUserRepository(SqlAlchemyTenantScopedRepository):
    """Load users only within the repository's bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create a user repository scoped to ``tenant_id``.

        Args:
            session: Async SQLAlchemy session.
            tenant_id: Tenant whose users may be read.
        """
        super().__init__(session, tenant_id)

    async def list_users(self) -> list[UserModel]:
        """Return all users belonging to the bound tenant."""
        statement = self._scoped(select(UserModel), UserModel)
        result = await self._session.scalars(statement)
        return list(result.all())

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        """Return a user by id if it belongs to the bound tenant.

        Args:
            user_id: Primary key of the user row.

        Returns:
            The user when found in this tenant; otherwise ``None`` (including
            when the row exists under a different tenant).
        """
        statement = self._scoped(
            select(UserModel).where(UserModel.id == user_id),
            UserModel,
        )
        result = await self._session.scalar(statement)
        return cast(UserModel | None, result)
