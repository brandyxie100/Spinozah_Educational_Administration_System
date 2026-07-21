"""Map invoice domain entities to ORM rows."""

from __future__ import annotations

from decimal import Decimal

from app.domain.finance.entities import Invoice, InvoiceLineItem, PaymentStatus
from app.infrastructure.persistence.invoice_models import (
    InvoiceModel,
    PaymentStatusDB,
)


def invoice_to_model(invoice: Invoice) -> InvoiceModel:
    """Convert a domain invoice into a persistence model."""
    return InvoiceModel(
        id=invoice.id,
        tenant_id=invoice.tenant_id,
        student_id=invoice.student_id,
        enrolment_id=invoice.enrolment_id,
        semester_label=invoice.semester_label,
        subtotal=invoice.subtotal,
        credit=invoice.credit,
        final_amount=invoice.final_amount,
        status=PaymentStatusDB(invoice.status.value),
        line_items=[
            {"description": item.description, "amount": str(item.amount)}
            for item in invoice.line_items
        ],
    )


def model_to_invoice(model: InvoiceModel) -> Invoice:
    """Convert a persistence row into a domain invoice."""
    items: list[InvoiceLineItem] = []
    for raw in model.line_items:
        items.append(
            InvoiceLineItem(
                description=str(raw["description"]),
                amount=Decimal(str(raw["amount"])),
            ),
        )
    return Invoice(
        id=model.id,
        tenant_id=model.tenant_id,
        student_id=model.student_id,
        enrolment_id=model.enrolment_id,
        semester_label=model.semester_label,
        subtotal=Decimal(model.subtotal),
        credit=Decimal(model.credit),
        status=PaymentStatus(model.status.value),
        line_items=items,
    )


def apply_invoice_to_model(model: InvoiceModel, invoice: Invoice) -> None:
    """Copy mutable invoice fields onto an existing ORM row."""
    model.subtotal = invoice.subtotal
    model.credit = invoice.credit
    model.final_amount = invoice.final_amount
    model.status = PaymentStatusDB(invoice.status.value)
    model.line_items = [
        {"description": item.description, "amount": str(item.amount)}
        for item in invoice.line_items
    ]
