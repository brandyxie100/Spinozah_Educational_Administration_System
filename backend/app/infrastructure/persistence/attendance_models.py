"""ORM model for attendance check-in records."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class AttendanceStatusDB(enum.StrEnum):
    """Persisted attendance lifecycle values."""

    PENDING_CONFIRMATION = "pending_confirmation"
    PRESENT = "present"
    ABSENT = "absent"


def _attendance_status_values(enum_cls: type[AttendanceStatusDB]) -> list[str]:
    """Return enum values for PostgreSQL ENUM creation."""
    return [member.value for member in enum_cls]


class AttendanceModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Lesson check-in scoped to a tenant; one row per schedule."""

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "schedule_id",
            name="uq_attendance_tenant_schedule",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrolment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrolments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[AttendanceStatusDB] = mapped_column(
        Enum(
            AttendanceStatusDB,
            name="attendance_status",
            values_callable=_attendance_status_values,
        ),
        nullable=False,
        default=AttendanceStatusDB.PENDING_CONFIRMATION,
    )
