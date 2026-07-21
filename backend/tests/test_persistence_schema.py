"""Unit tests for persistence schema metadata (no live database required)."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.session import create_engine


def test_tenant_and_user_tables_registered_on_metadata() -> None:
    """Baseline tables are present on the declarative metadata."""
    table_names = set(Base.metadata.tables.keys())
    assert "tenants" in table_names
    assert "users" in table_names


def test_user_model_requires_tenant_id_column() -> None:
    """Every user row is scoped to a tenant via tenant_id."""
    tenant_column = UserModel.__table__.c.tenant_id
    assert tenant_column.nullable is False
    assert tenant_column.foreign_keys


def test_user_role_enum_values_match_product_roles() -> None:
    """Role enum matches documented RBAC roles."""
    assert {role.value for role in UserRole} == {
        "admin",
        "frontdesk",
        "teacher",
        "parent",
    }


def test_create_engine_uses_async_postgres_driver() -> None:
    """Async engine URL uses the asyncpg dialect."""
    engine = create_engine()
    assert engine.url.drivername == "postgresql+asyncpg"
    assert TenantModel.__tablename__ == "tenants"
