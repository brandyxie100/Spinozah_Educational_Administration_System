"""ORM model for lesson schedules with optional weekly recurrence."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class ScheduleStatusDB(enum.StrEnum):
    """Persisted schedule lifecycle values."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


def _schedule_status_values(enum_cls: type[ScheduleStatusDB]) -> list[str]:
    """Return enum values for PostgreSQL ENUM creation."""
    return [member.value for member in enum_cls]


class ScheduleModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Lesson booking scoped to a tenant; optional weekly recurrence."""

    __tablename__ = "schedules"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    classroom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[ScheduleStatusDB] = mapped_column(
        Enum(
            ScheduleStatusDB,
            name="schedule_status",
            values_callable=_schedule_status_values,
        ),
        nullable=False,
        default=ScheduleStatusDB.NOT_STARTED,
    )
    # When true, recurrence_weekday + optional recurrence_until define the series.
    is_recurring: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=False,
    )
    recurrence_weekday: Mapped[int | None] = mapped_column(
        Integer(),
        nullable=True,
    )
    recurrence_until: Mapped[date | None] = mapped_column(Date(), nullable=True)
