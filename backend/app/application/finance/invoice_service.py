"""Application service for semester invoice generation and payment updates."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.domain.finance.entities import Invoice, InvoiceLineItem, PaymentStatus
from app.infrastructure.pdf.invoice_pdf import InvoicePdfGenerator
from app.infrastructure.persistence.student_models import StudentModel


class InvoiceRepositoryPort(Protocol):
    """Persistence port used by ``InvoiceService``."""

    @property
    def tenant_id(self) -> UUID:
        """Bound tenant id for all operations."""
        ...

    async def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        """Load one invoice in the tenant."""
        ...

    async def add(self, invoice: Invoice) -> Invoice:
        """Insert a new invoice."""
        ...

    async def save(self, invoice: Invoice) -> Invoice:
        """Update an existing invoice."""
        ...


class StudentLookupPort(Protocol):
    """Minimal student lookup for invoice generation."""

    async def get_by_id(self, student_id: UUID) -> StudentModel | None:
        """Return the student row or ``None``."""
        ...


class InvoiceNotFoundError(Exception):
    """Raised when an invoice id is missing in the tenant."""


class InvoiceStudentNotFoundError(Exception):
    """Raised when the student id is missing in the tenant."""


class InvoiceService:
    """Create semester invoices, update payment status, and export PDF."""

    def __init__(
        self,
        invoice_repository: InvoiceRepositoryPort,
        student_repository: StudentLookupPort,
        pdf_generator: InvoicePdfGenerator | None = None,
    ) -> None:
        """Bind repositories and optional PDF adapter."""
        self._invoices = invoice_repository
        self._students = student_repository
        self._pdf = pdf_generator or InvoicePdfGenerator()

    async def create_invoice(
        self,
        *,
        student_id: UUID,
        semester_label: str,
        subtotal: Decimal,
        credit: Decimal = Decimal("0.00"),
        line_items: list[dict[str, object]] | None = None,
        enrolment_id: UUID | None = None,
    ) -> Invoice:
        """Generate a semester invoice; ``final_amount = subtotal - credit``."""
        student = await self._students.get_by_id(student_id)
        if student is None:
            raise InvoiceStudentNotFoundError(f"Student not found: {student_id}")

        items = [
            InvoiceLineItem(
                description=str(raw["description"]),
                amount=Decimal(str(raw["amount"])),
            )
            for raw in (line_items or [])
        ]
        invoice = Invoice(
            tenant_id=self._invoices.tenant_id,
            student_id=student_id,
            semester_label=semester_label,
            subtotal=subtotal,
            credit=credit,
            enrolment_id=enrolment_id,
            line_items=items,
            status=PaymentStatus.UNPAID,
        )
        return await self._invoices.add(invoice)

    async def get_invoice(self, invoice_id: UUID) -> Invoice:
        """Return an invoice by id or raise."""
        invoice = await self._invoices.get_by_id(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(f"Invoice not found: {invoice_id}")
        return invoice

    async def update_payment_status(
        self,
        invoice_id: UUID,
        *,
        status: PaymentStatus,
    ) -> Invoice:
        """Track payment lifecycle (unpaid / partial / paid / void)."""
        invoice = await self.get_invoice(invoice_id)
        if status == PaymentStatus.PAID:
            invoice.mark_paid()
        elif status == PaymentStatus.PARTIAL:
            invoice.mark_partial()
        elif status == PaymentStatus.VOID:
            invoice.void()
        elif status == PaymentStatus.UNPAID:
            if invoice.status == PaymentStatus.VOID:
                raise ValueError("Cannot reopen a void invoice as unpaid")
            invoice.status = PaymentStatus.UNPAID
        else:
            raise ValueError(f"Unsupported payment status: {status}")
        return await self._invoices.save(invoice)

    async def render_pdf(self, invoice_id: UUID) -> bytes:
        """Export the invoice as ReportLab PDF bytes."""
        invoice = await self.get_invoice(invoice_id)
        student = await self._students.get_by_id(invoice.student_id)
        student_name = student.full_name if student is not None else "Unknown student"
        return self._pdf.render(invoice, student_name=student_name)
