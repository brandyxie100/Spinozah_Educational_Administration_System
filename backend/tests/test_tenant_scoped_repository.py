"""Unit tests for tenant-scoped query construction (no live database)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from app.infrastructure.persistence.models import TenantModel, UserModel
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)
from sqlalchemy import select


def test_scoped_statement_includes_tenant_id_predicate() -> None:
    """Compiled WHERE clause must constrain UserModel.tenant_id."""
    tenant_id = uuid.uuid4()
    repo = SqlAlchemyTenantScopedRepository(MagicMock(), tenant_id)
    statement = repo._scoped(select(UserModel), UserModel)
    compiled = str(statement.compile(compile_kwargs={"literal_binds": True}))

    assert "users.tenant_id" in compiled
    assert tenant_id.hex in compiled.replace("-", "")


def test_scoped_rejects_non_tenant_owned_model() -> None:
    """Tenant table itself has no tenant_id; scoping it must fail loudly."""
    repo = SqlAlchemyTenantScopedRepository(MagicMock(), uuid.uuid4())

    with pytest.raises(TypeError, match="not tenant-owned"):
        repo._scoped(select(TenantModel), TenantModel)
