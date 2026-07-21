"""Unit tests for parent dashboard scoping on ParentPortalService."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import app.application.parent_portal.magic_link_service as mod
import pytest
from app.application.parent_portal.dashboard_models import (
    EnrolmentNotFoundError,
    ParentInvoiceNotFoundError,
    ParentStudentNotLinkedError,
)
from app.application.parent_portal.magic_link_service import (
    CaptureMagicLinkMailer,
    ParentPortalService,
)
from app.domain.attendance import AttendanceRecord, AttendanceStatus
from app.domain.finance import Invoice, PaymentStatus
from app.domain.students import Enrolment
from app.infrastructure.security.jwt_token_service import JwtTokenService


def _service() -> ParentPortalService:
    return ParentPortalService(
        session=AsyncMock(),
        token_service=JwtTokenService(
            secret="test-secret-at-least-32-characters-long",
            access_expire_minutes=15,
            refresh_expire_days=7,
        ),
        mailer=CaptureMagicLinkMailer(),
    )


@pytest.mark.asyncio
async def test_unlinked_student_raises_on_dashboard_reads() -> None:
    service = _service()

    async def _assert_fail(**kwargs: object) -> None:
        raise ParentStudentNotLinkedError("Student not linked to parent")

    service._assert_student_linked = _assert_fail  # type: ignore[method-assign]

    with pytest.raises(ParentStudentNotLinkedError):
        await service.get_student_enrolment(
            tenant_id=uuid.uuid4(),
            parent_user_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_get_enrolment_and_lists_for_linked_student() -> None:
    student_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    service = _service()

    async def _ok(**kwargs: object) -> None:
        return None

    service._assert_student_linked = _ok  # type: ignore[method-assign]

    enrolment = Enrolment(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        total_lessons=20,
        completed_lessons=5,
    )
    attendance = [
        AttendanceRecord(
            tenant_id=tenant_id,
            schedule_id=uuid.uuid4(),
            student_id=student_id,
            enrolment_id=enrolment.id,
            status=AttendanceStatus.PRESENT,
        ),
    ]
    invoice = Invoice(
        tenant_id=tenant_id,
        student_id=student_id,
        semester_label="2026-S2",
        subtotal=Decimal("100.00"),
        status=PaymentStatus.UNPAID,
    )

    class _EnrolmentRepo:
        async def get_active_for_student(self, sid: uuid.UUID) -> Enrolment | None:
            return enrolment if sid == student_id else None

    class _AttendanceRepo:
        async def list_by_student_id(self, sid: uuid.UUID) -> list[AttendanceRecord]:
            return attendance

    class _InvoiceRepo:
        async def list_by_student_id(self, sid: uuid.UUID) -> list[Invoice]:
            return [invoice]

        async def get_by_id(self, invoice_id: uuid.UUID) -> Invoice | None:
            return invoice if invoice_id == invoice.id else None

    original_enrolment = mod.SqlAlchemyEnrolmentRepository
    original_attendance = mod.SqlAlchemyAttendanceRepository
    original_invoice = mod.SqlAlchemyInvoiceRepository
    mod.SqlAlchemyEnrolmentRepository = (  # type: ignore[misc,assignment]
        lambda *_a, **_k: _EnrolmentRepo()
    )
    mod.SqlAlchemyAttendanceRepository = (  # type: ignore[misc,assignment]
        lambda *_a, **_k: _AttendanceRepo()
    )
    mod.SqlAlchemyInvoiceRepository = (  # type: ignore[misc,assignment]
        lambda *_a, **_k: _InvoiceRepo()
    )
    try:
        view = await service.get_student_enrolment(
            tenant_id=tenant_id,
            parent_user_id=parent_id,
            student_id=student_id,
        )
        assert view.remaining_lessons == 15
        assert (
            len(
                await service.list_student_attendance(
                    tenant_id=tenant_id,
                    parent_user_id=parent_id,
                    student_id=student_id,
                ),
            )
            == 1
        )
        listed = await service.list_student_invoices(
            tenant_id=tenant_id,
            parent_user_id=parent_id,
            student_id=student_id,
        )
        assert listed[0].id == invoice.id
        got = await service.get_student_invoice(
            tenant_id=tenant_id,
            parent_user_id=parent_id,
            student_id=student_id,
            invoice_id=invoice.id,
        )
        assert got.final_amount == Decimal("100.00")
        report = await service.get_student_dashboard_report(
            tenant_id=tenant_id,
            parent_user_id=parent_id,
            student_id=student_id,
        )
        assert report.unpaid_invoice_count == 1
        assert report.remaining_lessons == 15
    finally:
        mod.SqlAlchemyEnrolmentRepository = original_enrolment  # type: ignore[misc]
        mod.SqlAlchemyAttendanceRepository = original_attendance  # type: ignore[misc]
        mod.SqlAlchemyInvoiceRepository = original_invoice  # type: ignore[misc]


@pytest.mark.asyncio
async def test_missing_enrolment_and_wrong_invoice_raise() -> None:
    student_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    service = _service()

    async def _ok(**kwargs: object) -> None:
        return None

    service._assert_student_linked = _ok  # type: ignore[method-assign]

    class _EnrolmentRepo:
        async def get_active_for_student(self, sid: uuid.UUID) -> None:
            return None

    class _InvoiceRepo:
        async def get_by_id(self, invoice_id: uuid.UUID) -> Invoice | None:
            return Invoice(
                tenant_id=tenant_id,
                student_id=uuid.uuid4(),
                semester_label="x",
                subtotal=Decimal("1.00"),
            )

    original_enrolment = mod.SqlAlchemyEnrolmentRepository
    original_invoice = mod.SqlAlchemyInvoiceRepository
    mod.SqlAlchemyEnrolmentRepository = (  # type: ignore[misc,assignment]
        lambda *_a, **_k: _EnrolmentRepo()
    )
    mod.SqlAlchemyInvoiceRepository = (  # type: ignore[misc,assignment]
        lambda *_a, **_k: _InvoiceRepo()
    )
    try:
        with pytest.raises(EnrolmentNotFoundError):
            await service.get_student_enrolment(
                tenant_id=tenant_id,
                parent_user_id=uuid.uuid4(),
                student_id=student_id,
            )
        with pytest.raises(ParentInvoiceNotFoundError):
            await service.get_student_invoice(
                tenant_id=tenant_id,
                parent_user_id=uuid.uuid4(),
                student_id=student_id,
                invoice_id=uuid.uuid4(),
            )
    finally:
        mod.SqlAlchemyEnrolmentRepository = original_enrolment  # type: ignore[misc]
        mod.SqlAlchemyInvoiceRepository = original_invoice  # type: ignore[misc]
