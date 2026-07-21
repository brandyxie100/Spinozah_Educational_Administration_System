"""Invoice domain entity with payment status and amount formula."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4


class PaymentStatus(StrEnum):
    """Invoice payment lifecycle."""

    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    VOID = "void"


@dataclass(frozen=True, slots=True)
class InvoiceLineItem:
    """One billable line on a semester invoice."""

    description: str
    amount: Decimal

    def __post_init__(self) -> None:
        """Require a non-empty description and non-negative amount."""
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if self.amount < 0:
            raise ValueError("line amount must be non-negative")


@dataclass(slots=True)
class Invoice:
    """Semester tuition invoice; ``final_amount = subtotal - credit``."""

    tenant_id: UUID
    student_id: UUID
    semester_label: str
    subtotal: Decimal
    credit: Decimal = Decimal("0.00")
    status: PaymentStatus = PaymentStatus.UNPAID
    enrolment_id: UUID | None = None
    line_items: list[InvoiceLineItem] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Validate amounts and semester label."""
        if not self.semester_label.strip():
            raise ValueError("semester_label must not be empty")
        if self.subtotal < 0:
            raise ValueError("subtotal must be non-negative")
        if self.credit < 0:
            raise ValueError("credit must be non-negative")
        if self.credit > self.subtotal:
            raise ValueError("credit cannot exceed subtotal")

    @property
    def final_amount(self) -> Decimal:
        """Amount due after credit: ``subtotal - credit``."""
        return self.subtotal - self.credit

    def mark_paid(self) -> None:
        """Mark the invoice fully paid."""
        if self.status == PaymentStatus.VOID:
            raise ValueError("Cannot pay a void invoice")
        self.status = PaymentStatus.PAID

    def mark_partial(self) -> None:
        """Mark the invoice as partially paid."""
        if self.status == PaymentStatus.VOID:
            raise ValueError("Cannot pay a void invoice")
        if self.status == PaymentStatus.PAID:
            raise ValueError("Invoice is already fully paid")
        self.status = PaymentStatus.PARTIAL

    def void(self) -> None:
        """Void the invoice (no further payment)."""
        if self.status == PaymentStatus.PAID:
            raise ValueError("Cannot void a paid invoice")
        self.status = PaymentStatus.VOID
