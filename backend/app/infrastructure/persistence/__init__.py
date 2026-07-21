"""Persistence adapters (SQLAlchemy models and session factory)."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.session import (
    create_engine,
    create_session_factory,
    get_session,
)
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository

__all__ = [
    "Base",
    "SqlAlchemyTenantScopedRepository",
    "SqlAlchemyUserRepository",
    "TenantModel",
    "UserModel",
    "UserRole",
    "create_engine",
    "create_session_factory",
    "get_session",
]
