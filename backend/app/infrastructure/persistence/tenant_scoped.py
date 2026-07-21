"""SQLAlchemy helpers that enforce tenant_id on every repository query."""

from __future__ import annotations

from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.domain.shared.repositories import TenantScopedRepository

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class SqlAlchemyTenantScopedRepository(TenantScopedRepository):
    """Base class for ORM repositories that always scope by tenant_id.

    Subclasses must pass every ``select()`` through :meth:`_scoped` so the
    tenant filter cannot be omitted by accident.
    """

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Bind this repository to a session and a single tenant.

        Args:
            session: Async SQLAlchemy session for the unit of work.
            tenant_id: Tenant that owns all rows visible through this repo.
        """
        self._session = session
        self._tenant_id = tenant_id

    @property
    def tenant_id(self) -> UUID:
        """Identifier of the tenant that owns visible rows."""
        return self._tenant_id

    def _scoped(self, statement: Select[Any], model: type[ModelT]) -> Select[Any]:
        """Apply the mandatory ``tenant_id`` filter to a select statement.

        Args:
            statement: Base select (may already include other WHERE clauses).
            model: ORM model that owns a ``tenant_id`` column.

        Returns:
            The same statement with ``model.tenant_id == self.tenant_id``.

        Raises:
            TypeError: If ``model`` is not tenant-owned (no ``tenant_id``).
        """
        # Critical: every query path must go through this helper.
        tenant_column = getattr(model, "tenant_id", None)
        if tenant_column is None:
            msg = f"{model.__name__} is not tenant-owned; cannot scope by tenant"
            raise TypeError(msg)
        return statement.where(tenant_column == self._tenant_id)
