"""Semester invoice generation, payment status, and PDF export endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.invoice_schemas import (
    InvoiceCreate,
    InvoiceLineItemOut,
    InvoiceOut,
    InvoicePaymentStatusUpdate,
)
from app.application.finance.invoice_service import (
    InvoiceNotFoundError,
    InvoiceService,
    InvoiceStudentNotFoundError,
)
from app.domain.finance.entities import Invoice, PaymentStatus
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.invoice_repository import (
    SqlAlchemyInvoiceRepository,
)
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])


def get_invoice_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
) -> InvoiceService:
    """Compose invoice service scoped to the caller's tenant."""
    return InvoiceService(
        invoice_repository=SqlAlchemyInvoiceRepository(session, claims.tenant_id),
        student_repository=SqlAlchemyStudentRepository(session, claims.tenant_id),
    )


def _to_out(invoice: Invoice) -> InvoiceOut:
    return InvoiceOut(
        id=invoice.id,
        tenant_id=invoice.tenant_id,
        student_id=invoice.student_id,
        enrolment_id=invoice.enrolment_id,
        semester_label=invoice.semester_label,
        subtotal=invoice.subtotal,
        credit=invoice.credit,
        final_amount=invoice.final_amount,
        status=invoice.status.value,
        line_items=[
            InvoiceLineItemOut(description=item.description, amount=item.amount)
            for item in invoice.line_items
        ],
    )


@router.post("", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    body: InvoiceCreate,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> InvoiceOut:
    """Generate a semester invoice; final_amount = subtotal - credit."""
    try:
        invoice = await service.create_invoice(
            student_id=body.student_id,
            semester_label=body.semester_label,
            subtotal=body.subtotal,
            credit=body.credit,
            enrolment_id=body.enrolment_id,
            line_items=[item.model_dump() for item in body.line_items],
        )
    except InvoiceStudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return _to_out(invoice)


@router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: UUID,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> InvoiceOut:
    """Fetch one invoice by id within the caller's tenant."""
    try:
        invoice = await service.get_invoice(invoice_id)
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _to_out(invoice)


@router.patch("/{invoice_id}/payment-status", response_model=InvoiceOut)
async def update_payment_status(
    invoice_id: UUID,
    body: InvoicePaymentStatusUpdate,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> InvoiceOut:
    """Update payment tracking status for an invoice."""
    try:
        invoice = await service.update_payment_status(
            invoice_id,
            status=PaymentStatus(body.status),
        )
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return _to_out(invoice)


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: UUID,
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
) -> Response:
    """Export the invoice as a ReportLab-generated PDF document."""
    try:
        pdf_bytes = await service.render_pdf(invoice_id)
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="invoice-{invoice_id}.pdf"',
        },
    )
