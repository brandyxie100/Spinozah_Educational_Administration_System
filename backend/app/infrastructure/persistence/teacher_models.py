"""ORM model for teachers."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class TeacherModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Instructor profile scoped to a tenant; optional user account link."""

    __tablename__ = "teachers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_teachers_tenant_email"),
        UniqueConstraint("tenant_id", "user_id", name="uq_teachers_tenant_user"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    # Optional link to identity.users for login; null when profile-only.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
