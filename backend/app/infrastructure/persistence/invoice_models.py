"""ORM models for invoices."""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class PaymentStatusDB(enum.StrEnum):
    """Persisted invoice payment lifecycle."""

    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    VOID = "void"


def _payment_status_values(enum_cls: type[PaymentStatusDB]) -> list[str]:
    return [member.value for member in enum_cls]


class InvoiceModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Semester invoice scoped to a tenant student."""

    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "student_id",
            "semester_label",
            name="uq_invoices_tenant_student_semester",
        ),
    )

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
    enrolment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrolments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    semester_label: Mapped[str] = mapped_column(String(100), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    credit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    # Stored for query convenience; always equals subtotal - credit.
    final_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[PaymentStatusDB] = mapped_column(
        Enum(
            PaymentStatusDB,
            name="payment_status",
            values_callable=_payment_status_values,
        ),
        nullable=False,
        default=PaymentStatusDB.UNPAID,
    )
    line_items: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
