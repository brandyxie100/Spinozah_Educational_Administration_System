"""ORM models for students and enrolments."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class EnrolmentStatusDB(enum.StrEnum):
    """Persisted enrolment lifecycle values."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def _enrolment_status_values(enum_cls: type[EnrolmentStatusDB]) -> list[str]:
    """Return enum values for PostgreSQL ENUM creation."""
    return [member.value for member in enum_cls]


class StudentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Learner profile scoped to a tenant."""

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_students_tenant_email"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    enrolments: Mapped[list[EnrolmentModel]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )


class EnrolmentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Lesson package for a student; tracks total/completed lessons."""

    __tablename__ = "enrolments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    total_lessons: Mapped[int] = mapped_column(Integer(), nullable=False)
    completed_lessons: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
    )
    extension_days: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
    )
    status: Mapped[EnrolmentStatusDB] = mapped_column(
        Enum(
            EnrolmentStatusDB,
            name="enrolment_status",
            values_callable=_enrolment_status_values,
        ),
        nullable=False,
        default=EnrolmentStatusDB.ACTIVE,
    )

    student: Mapped[StudentModel] = relationship(back_populates="enrolments")
