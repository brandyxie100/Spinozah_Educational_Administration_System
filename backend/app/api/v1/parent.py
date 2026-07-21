"""Parent portal magic-link auth and dashboard read endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_token_service, require_roles
from app.api.v1.auth import _set_refresh_cookie, _to_token_response
from app.api.v1.auth_schemas import TokenResponse
from app.api.v1.parent_schemas import (
    LinkedStudentOut,
    MagicLinkConsumeRequest,
    MagicLinkRequest,
    MagicLinkRequestResponse,
    ParentAttendanceOut,
    ParentDashboardReportOut,
    ParentEnrolmentOut,
    ParentInvoiceOut,
    ParentStudentLinkCreate,
    ParentStudentLinkOut,
)
from app.application.parent_portal.magic_link_service import (
    EnrolmentNotFoundError,
    NotAParentError,
    ParentInvoiceNotFoundError,
    ParentNotFoundError,
    ParentPortalService,
    ParentStudentNotLinkedError,
    StudentNotFoundError,
)
from app.core.settings import Settings, get_settings
from app.domain.finance.entities import Invoice
from app.domain.identity.exceptions import InvalidCredentialsError
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.email.magic_link_mailer import LoggingMagicLinkMailer
from app.infrastructure.persistence.session import get_session
from app.infrastructure.security.jwt_token_service import JwtTokenService

router = APIRouter(prefix="/api/v1/parent", tags=["parent-portal"])


def get_parent_portal_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[JwtTokenService, Depends(get_token_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ParentPortalService:
    """Compose parent portal service for magic-link and dashboard reads."""
    return ParentPortalService(
        session=session,
        token_service=token_service,
        mailer=LoggingMagicLinkMailer(),
        magic_link_ttl_minutes=settings.magic_link_expire_minutes,
        magic_link_base_url=settings.magic_link_base_url,
        expose_magic_url=settings.debug,
    )


def _invoice_out(invoice: Invoice) -> ParentInvoiceOut:
    return ParentInvoiceOut(
        id=invoice.id,
        student_id=invoice.student_id,
        semester_label=invoice.semester_label,
        subtotal=invoice.subtotal,
        credit=invoice.credit,
        final_amount=invoice.final_amount,
        status=invoice.status.value,
    )


@router.post(
    "/magic-link/request",
    response_model=MagicLinkRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_magic_link(
    body: MagicLinkRequest,
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> MagicLinkRequestResponse:
    """Email a one-time magic link for parent login (anti-enumeration)."""
    result = await service.request_magic_link(
        tenant_slug=body.tenant_slug,
        email=str(body.email),
    )
    return MagicLinkRequestResponse(magic_url=result.magic_url)


@router.post("/magic-link/consume", response_model=TokenResponse)
async def consume_magic_link(
    body: MagicLinkConsumeRequest,
    response: Response,
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Exchange a magic-link token for access JWT + refresh cookie."""
    try:
        tokens = await service.consume_magic_link(raw_token=body.token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    _set_refresh_cookie(response, tokens.refresh_token, settings)
    return _to_token_response(tokens)


@router.post(
    "/student-links",
    response_model=ParentStudentLinkOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_student_link(
    body: ParentStudentLinkCreate,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> ParentStudentLinkOut:
    """Link a parent user to a student (required for portal scoping)."""
    try:
        link = await service.link_student(
            tenant_id=claims.tenant_id,
            parent_user_id=body.parent_user_id,
            student_id=body.student_id,
        )
    except ParentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except StudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except NotAParentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return ParentStudentLinkOut(
        id=link.id,
        tenant_id=link.tenant_id,
        parent_user_id=link.parent_user_id,
        student_id=link.student_id,
    )


@router.get("/students", response_model=list[LinkedStudentOut])
async def list_linked_students(
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> list[LinkedStudentOut]:
    """Return students linked to the authenticated parent only."""
    rows = await service.list_linked_students(
        tenant_id=claims.tenant_id,
        parent_user_id=claims.user_id,
    )
    return [
        LinkedStudentOut(
            id=row.id,
            full_name=row.full_name,
            email=row.email,
            is_active=row.is_active,
        )
        for row in rows
    ]


@router.get(
    "/students/{student_id}/enrolment",
    response_model=ParentEnrolmentOut,
)
async def get_student_enrolment(
    student_id: UUID,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> ParentEnrolmentOut:
    """Return remaining lessons for a linked student."""
    try:
        view = await service.get_student_enrolment(
            tenant_id=claims.tenant_id,
            parent_user_id=claims.user_id,
            student_id=student_id,
        )
    except ParentStudentNotLinkedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EnrolmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    enrolment = view.enrolment
    return ParentEnrolmentOut(
        id=enrolment.id,
        student_id=enrolment.student_id,
        status=enrolment.status.value,
        total_lessons=enrolment.total_lessons,
        completed_lessons=enrolment.completed_lessons,
        remaining_lessons=view.remaining_lessons,
        extension_days=enrolment.extension_days,
    )


@router.get(
    "/students/{student_id}/attendance",
    response_model=list[ParentAttendanceOut],
)
async def list_student_attendance(
    student_id: UUID,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> list[ParentAttendanceOut]:
    """Return attendance history for a linked student."""
    try:
        rows = await service.list_student_attendance(
            tenant_id=claims.tenant_id,
            parent_user_id=claims.user_id,
            student_id=student_id,
        )
    except ParentStudentNotLinkedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return [
        ParentAttendanceOut(
            id=row.id,
            schedule_id=row.schedule_id,
            student_id=row.student_id,
            enrolment_id=row.enrolment_id,
            status=row.status.value,
        )
        for row in rows
    ]


@router.get(
    "/students/{student_id}/invoices",
    response_model=list[ParentInvoiceOut],
)
async def list_student_invoices(
    student_id: UUID,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> list[ParentInvoiceOut]:
    """Return invoices for a linked student."""
    try:
        invoices = await service.list_student_invoices(
            tenant_id=claims.tenant_id,
            parent_user_id=claims.user_id,
            student_id=student_id,
        )
    except ParentStudentNotLinkedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return [_invoice_out(invoice) for invoice in invoices]


@router.get(
    "/students/{student_id}/invoices/{invoice_id}",
    response_model=ParentInvoiceOut,
)
async def get_student_invoice(
    student_id: UUID,
    invoice_id: UUID,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> ParentInvoiceOut:
    """Return one invoice for a linked student."""
    try:
        invoice = await service.get_student_invoice(
            tenant_id=claims.tenant_id,
            parent_user_id=claims.user_id,
            student_id=student_id,
            invoice_id=invoice_id,
        )
    except ParentStudentNotLinkedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ParentInvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _invoice_out(invoice)


@router.get("/students/{student_id}/invoices/{invoice_id}/pdf")
async def download_student_invoice_pdf(
    student_id: UUID,
    invoice_id: UUID,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> Response:
    """Download a linked student's invoice PDF."""
    try:
        pdf_bytes = await service.render_student_invoice_pdf(
            tenant_id=claims.tenant_id,
            parent_user_id=claims.user_id,
            student_id=student_id,
            invoice_id=invoice_id,
        )
    except ParentStudentNotLinkedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ParentInvoiceNotFoundError as exc:
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


@router.get(
    "/students/{student_id}/report",
    response_model=ParentDashboardReportOut,
)
async def get_student_dashboard_report(
    student_id: UUID,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> ParentDashboardReportOut:
    """Return an aggregate dashboard report for a linked student."""
    try:
        report = await service.get_student_dashboard_report(
            tenant_id=claims.tenant_id,
            parent_user_id=claims.user_id,
            student_id=student_id,
        )
    except ParentStudentNotLinkedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return ParentDashboardReportOut(
        student_id=report.student_id,
        remaining_lessons=report.remaining_lessons,
        total_lessons=report.total_lessons,
        completed_lessons=report.completed_lessons,
        attendance_count=report.attendance_count,
        invoice_count=report.invoice_count,
        unpaid_invoice_count=report.unpaid_invoice_count,
    )
