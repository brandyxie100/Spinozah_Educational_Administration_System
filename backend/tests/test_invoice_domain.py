"""Domain unit tests for invoice amounts and payment status."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from app.domain.finance import Invoice, InvoiceLineItem, PaymentStatus


def test_final_amount_equals_subtotal_minus_credit() -> None:
    invoice = Invoice(
        tenant_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        semester_label="2026-S2",
        subtotal=Decimal("1200.00"),
        credit=Decimal("150.00"),
    )
    assert invoice.final_amount == Decimal("1050.00")


def test_credit_cannot_exceed_subtotal() -> None:
    with pytest.raises(ValueError, match="credit cannot exceed subtotal"):
        Invoice(
            tenant_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            semester_label="2026-S2",
            subtotal=Decimal("100.00"),
            credit=Decimal("101.00"),
        )


def test_mark_paid_updates_payment_status() -> None:
    invoice = Invoice(
        tenant_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        semester_label="2026-S2",
        subtotal=Decimal("500.00"),
    )
    assert invoice.status == PaymentStatus.UNPAID
    invoice.mark_paid()
    assert invoice.status == PaymentStatus.PAID


def test_cannot_void_paid_invoice() -> None:
    invoice = Invoice(
        tenant_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        semester_label="2026-S2",
        subtotal=Decimal("500.00"),
    )
    invoice.mark_paid()
    with pytest.raises(ValueError, match="Cannot void a paid invoice"):
        invoice.void()


def test_line_item_requires_description() -> None:
    with pytest.raises(ValueError, match="description must not be empty"):
        InvoiceLineItem(description="  ", amount=Decimal("10.00"))


def test_line_item_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="line amount must be non-negative"):
        InvoiceLineItem(description="Piano", amount=Decimal("-1.00"))


def test_invoice_rejects_empty_semester_and_negative_amounts() -> None:
    with pytest.raises(ValueError, match="semester_label must not be empty"):
        Invoice(
            tenant_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            semester_label=" ",
            subtotal=Decimal("10.00"),
        )
    with pytest.raises(ValueError, match="subtotal must be non-negative"):
        Invoice(
            tenant_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            semester_label="2026-S2",
            subtotal=Decimal("-1.00"),
        )
    with pytest.raises(ValueError, match="credit must be non-negative"):
        Invoice(
            tenant_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            semester_label="2026-S2",
            subtotal=Decimal("10.00"),
            credit=Decimal("-1.00"),
        )


def test_cannot_pay_void_invoice() -> None:
    invoice = Invoice(
        tenant_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        semester_label="2026-S2",
        subtotal=Decimal("500.00"),
    )
    invoice.void()
    with pytest.raises(ValueError, match="Cannot pay a void invoice"):
        invoice.mark_paid()
    with pytest.raises(ValueError, match="Cannot pay a void invoice"):
        invoice.mark_partial()


def test_mark_partial_and_reject_when_already_paid() -> None:
    invoice = Invoice(
        tenant_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        semester_label="2026-S2",
        subtotal=Decimal("500.00"),
    )
    invoice.mark_partial()
    assert invoice.status == PaymentStatus.PARTIAL
    invoice.mark_paid()
    with pytest.raises(ValueError, match="already fully paid"):
        invoice.mark_partial()
