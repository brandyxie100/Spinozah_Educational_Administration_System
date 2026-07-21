"""ORM models for tenants and users (identity baseline)."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class UserRole(enum.StrEnum):
    """Application roles enforced by RBAC (AIJOB-36)."""

    ADMIN = "admin"
    FRONTDESK = "frontdesk"
    TEACHER = "teacher"
    PARENT = "parent"


def _role_values(enum_cls: type[UserRole]) -> list[str]:
    """Return enum values for PostgreSQL ENUM creation."""
    return [member.value for member in enum_cls]


class TenantModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Multi-tenant organization (tutoring center)."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    users: Mapped[list[UserModel]] = relationship(back_populates="tenant")


class UserModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Platform user belonging to a single tenant."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=_role_values),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    tenant: Mapped[TenantModel] = relationship(back_populates="users")
