"""ORM model for leave requests."""

from __future__ import annotations

import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class LeaveKindDB(enum.StrEnum):
    """Persisted leave categories."""

    SICK = "sick"
    PERSONAL = "personal"


class LeaveStatusDB(enum.StrEnum):
    """Persisted leave workflow states."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def _leave_kind_values(enum_cls: type[LeaveKindDB]) -> list[str]:
    return [member.value for member in enum_cls]


def _leave_status_values(enum_cls: type[LeaveStatusDB]) -> list[str]:
    return [member.value for member in enum_cls]


class LeaveRequestModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Leave request scoped to a tenant enrolment."""

    __tablename__ = "leave_requests"

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
    enrolment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrolments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    leave_date: Mapped[date] = mapped_column(Date(), nullable=False)
    kind: Mapped[LeaveKindDB] = mapped_column(
        Enum(LeaveKindDB, name="leave_kind", values_callable=_leave_kind_values),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[LeaveStatusDB] = mapped_column(
        Enum(
            LeaveStatusDB,
            name="leave_status",
            values_callable=_leave_status_values,
        ),
        nullable=False,
        default=LeaveStatusDB.PENDING,
    )
    is_free: Mapped[bool | None] = mapped_column(Boolean(), nullable=True)
    extension_days_applied: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
    )
