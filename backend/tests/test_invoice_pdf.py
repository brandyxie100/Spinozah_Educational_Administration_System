"""Unit tests for ReportLab invoice PDF generation."""

from __future__ import annotations

import uuid
from decimal import Decimal

from app.domain.finance import Invoice, InvoiceLineItem
from app.infrastructure.pdf.invoice_pdf import InvoicePdfGenerator


def test_invoice_pdf_render_returns_non_empty_pdf_bytes() -> None:
    invoice = Invoice(
        tenant_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        semester_label="2026-S2",
        subtotal=Decimal("800.00"),
        credit=Decimal("50.00"),
        line_items=[
            InvoiceLineItem(description="Piano", amount=Decimal("500.00")),
            InvoiceLineItem(description="Theory", amount=Decimal("300.00")),
        ],
    )
    pdf = InvoicePdfGenerator().render(invoice, student_name="Ada Lovelace")
    assert isinstance(pdf, bytes)
    assert len(pdf) > 100
    assert pdf.startswith(b"%PDF")
