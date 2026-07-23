"""ORM models for persisted AI analysis reports."""

from __future__ import annotations

import enum
import uuid
from typing import Any

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class AnalysisKindDB(enum.StrEnum):
    """Persisted analysis kind values."""

    EXAM = "exam"
    ESSAY = "essay"


def _analysis_kind_values(enum_cls: type[AnalysisKindDB]) -> list[str]:
    """Return enum values for PostgreSQL ENUM creation."""
    return [member.value for member in enum_cls]


class AnalysisRecordModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tenant-scoped exam/essay analysis snapshot."""

    __tablename__ = "analysis_records"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    kind: Mapped[AnalysisKindDB] = mapped_column(
        Enum(
            AnalysisKindDB,
            name="analysis_kind",
            values_callable=_analysis_kind_values,
        ),
        nullable=False,
        index=True,
    )
    student_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
