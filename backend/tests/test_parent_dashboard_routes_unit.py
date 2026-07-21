"""Unit tests for parent dashboard API routes with JWT + service override."""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from decimal import Decimal
from urllib.parse import parse_qs, urlparse

import pytest
from app.api.v1.parent import get_parent_portal_service
from app.application.identity.auth_service import AuthenticatedUser, AuthTokens
from app.application.parent_portal.dashboard_models import (
    ParentEnrolmentView,
    ParentStudentNotLinkedError,
    StudentDashboardReport,
)
from app.application.parent_portal.magic_link_service import (
    LinkedStudentSummary,
    MagicLinkRequestResult,
    ParentPortalService,
)
from app.domain.attendance import AttendanceRecord, AttendanceStatus
from app.domain.finance import Invoice
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.domain.parent_portal import ParentStudentLink
from app.domain.students import Enrolment
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.main import create_app
from fastapi.testclient import TestClient

SECRET = "parent-dashboard-test-secret-32chars!!"


class _FakeParentPortalService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self.parent_user_id = uuid.uuid4()
        self.linked_student_id = uuid.uuid4()
        self._token = "opaque-magic-token-value-123456"
        self._linked: list[LinkedStudentSummary] = [
            LinkedStudentSummary(
                id=self.linked_student_id,
                full_name="Ada",
                email=None,
                is_active=True,
            ),
        ]
        self._enrolment = Enrolment(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            student_id=self.linked_student_id,
            total_lessons=20,
            completed_lessons=4,
        )
        self._invoice = Invoice(
            tenant_id=self.tenant_id,
            student_id=self.linked_student_id,
            semester_label="2026-S2",
            subtotal=Decimal("500.00"),
            credit=Decimal("50.00"),
        )

    async def request_magic_link(self, **kwargs: object) -> MagicLinkRequestResult:
        return MagicLinkRequestResult(
            accepted=True,
            magic_url=(
                "http://localhost:3000/parent/magic-link"
                f"?token={self._token}&tenant={kwargs['tenant_slug']}"
            ),
        )

    async def consume_magic_link(self, *, raw_token: str) -> AuthTokens:
        assert raw_token == self._token
        user = AuthenticatedUser(
            id=self.parent_user_id,
            tenant_id=self.tenant_id,
            email="parent@example.com",
            full_name="Pat Parent",
            role="parent",
        )
        return AuthTokens(
            access_token="access.jwt",
            refresh_token="refresh.jwt",
            user=user,
        )

    async def link_student(self, **kwargs: object) -> ParentStudentLink:
        return ParentStudentLink(
            tenant_id=kwargs["tenant_id"],  # type: ignore[arg-type]
            parent_user_id=kwargs["parent_user_id"],  # type: ignore[arg-type]
            student_id=kwargs["student_id"],  # type: ignore[arg-type]
        )

    async def list_linked_students(
        self,
        **kwargs: object,
    ) -> list[LinkedStudentSummary]:
        return self._linked

    async def get_student_enrolment(self, **kwargs: object) -> ParentEnrolmentView:
        if kwargs["student_id"] != self.linked_student_id:
            raise ParentStudentNotLinkedError("not linked")
        return ParentEnrolmentView(
            enrolment=self._enrolment,
            remaining_lessons=self._enrolment.remaining_lessons(),
        )

    async def list_student_attendance(
        self,
        **kwargs: object,
    ) -> list[AttendanceRecord]:
        if kwargs["student_id"] != self.linked_student_id:
            raise ParentStudentNotLinkedError("not linked")
        return [
            AttendanceRecord(
                tenant_id=self.tenant_id,
                schedule_id=uuid.uuid4(),
                student_id=self.linked_student_id,
                enrolment_id=self._enrolment.id,
                status=AttendanceStatus.PRESENT,
            ),
        ]

    async def list_student_invoices(self, **kwargs: object) -> list[Invoice]:
        if kwargs["student_id"] != self.linked_student_id:
            raise ParentStudentNotLinkedError("not linked")
        return [self._invoice]

    async def get_student_invoice(self, **kwargs: object) -> Invoice:
        if kwargs["student_id"] != self.linked_student_id:
            raise ParentStudentNotLinkedError("not linked")
        return self._invoice

    async def render_student_invoice_pdf(self, **kwargs: object) -> bytes:
        await self.get_student_invoice(**kwargs)
        return b"%PDF-1.4 parent-invoice"

    async def get_student_dashboard_report(
        self,
        **kwargs: object,
    ) -> StudentDashboardReport:
        if kwargs["student_id"] != self.linked_student_id:
            raise ParentStudentNotLinkedError("not linked")
        return StudentDashboardReport(
            student_id=self.linked_student_id,
            remaining_lessons=16,
            total_lessons=20,
            completed_lessons=4,
            attendance_count=1,
            invoice_count=1,
            unpaid_invoice_count=1,
        )


@pytest.fixture
def client() -> Iterator[tuple[TestClient, _FakeParentPortalService]]:
    previous = os.environ.get("JWT_SECRET")
    os.environ["JWT_SECRET"] = SECRET
    fake = _FakeParentPortalService()
    app = create_app()

    def _override() -> ParentPortalService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_parent_portal_service] = _override
    with TestClient(app) as test_client:
        yield test_client, fake
    app.dependency_overrides.clear()
    if previous is None:
        os.environ.pop("JWT_SECRET", None)
    else:
        os.environ["JWT_SECRET"] = previous


def _parent_headers(fake: _FakeParentPortalService) -> dict[str, str]:
    token = JwtTokenService(
        secret=SECRET,
        access_expire_minutes=15,
        refresh_expire_days=7,
    ).create_access_token(
        AccessTokenClaims(
            user_id=fake.parent_user_id,
            tenant_id=fake.tenant_id,
            email="parent@example.com",
            role=Role.PARENT.value,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def test_magic_link_request_and_consume(
    client: tuple[TestClient, _FakeParentPortalService],
) -> None:
    test_client, _fake = client
    requested = test_client.post(
        "/api/v1/parent/magic-link/request",
        json={"tenant_slug": "acme", "email": "parent@example.com"},
    )
    assert requested.status_code == 202
    magic_url = requested.json()["magic_url"]
    assert magic_url is not None
    raw_token = parse_qs(urlparse(magic_url).query)["token"][0]

    consumed = test_client.post(
        "/api/v1/parent/magic-link/consume",
        json={"token": raw_token},
    )
    assert consumed.status_code == 200
    assert consumed.json()["user"]["role"] == "parent"


def test_dashboard_reads_for_linked_student(
    client: tuple[TestClient, _FakeParentPortalService],
) -> None:
    test_client, fake = client
    headers = _parent_headers(fake)
    sid = fake.linked_student_id

    enrolment = test_client.get(
        f"/api/v1/parent/students/{sid}/enrolment",
        headers=headers,
    )
    assert enrolment.status_code == 200
    assert enrolment.json()["remaining_lessons"] == 16

    attendance = test_client.get(
        f"/api/v1/parent/students/{sid}/attendance",
        headers=headers,
    )
    assert attendance.status_code == 200
    assert len(attendance.json()) == 1

    invoices = test_client.get(
        f"/api/v1/parent/students/{sid}/invoices",
        headers=headers,
    )
    assert invoices.status_code == 200
    assert invoices.json()[0]["final_amount"] == "450.00"

    report = test_client.get(
        f"/api/v1/parent/students/{sid}/report",
        headers=headers,
    )
    assert report.status_code == 200
    assert report.json()["unpaid_invoice_count"] == 1

    pdf = test_client.get(
        f"/api/v1/parent/students/{sid}/invoices/{fake._invoice.id}/pdf",
        headers=headers,
    )
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")


def test_unlinked_student_returns_404(
    client: tuple[TestClient, _FakeParentPortalService],
) -> None:
    test_client, fake = client
    headers = _parent_headers(fake)
    other = uuid.uuid4()
    response = test_client.get(
        f"/api/v1/parent/students/{other}/enrolment",
        headers=headers,
    )
    assert response.status_code == 404


def test_get_invoice_for_linked_student(
    client: tuple[TestClient, _FakeParentPortalService],
) -> None:
    test_client, fake = client
    headers = _parent_headers(fake)
    sid = fake.linked_student_id
    response = test_client.get(
        f"/api/v1/parent/students/{sid}/invoices/{fake._invoice.id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["semester_label"] == "2026-S2"
