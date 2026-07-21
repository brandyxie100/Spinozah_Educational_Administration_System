"""Unit tests for admin KPI routes with dependency overrides."""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from app.api.v1.admin_kpis import get_admin_kpi_service
from app.application.admin.kpi_models import (
    AdminKpiSnapshot,
    RevenuePeriodBucket,
    TodayScheduleItem,
)
from app.application.admin.kpi_service import AdminKpiService
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.main import create_app
from fastapi.testclient import TestClient

SECRET = "admin-kpi-unit-test-secret-32chars!!"


class _FakeAdminKpiService:
    async def get_kpis(self, *, on_date: object = None) -> AdminKpiSnapshot:
        return AdminKpiSnapshot(
            student_count=10,
            teacher_count=4,
            today_schedule_count=2,
            unpaid_invoice_count=3,
            unpaid_invoice_total=Decimal("450.00"),
            revenue_final_amount_sum=Decimal("1200.00"),
            revenue_by_period=[
                RevenuePeriodBucket(period="2026-S1", amount=Decimal("1200.00")),
            ],
            today_schedules=[
                TodayScheduleItem(
                    schedule_id=uuid.uuid4(),
                    teacher_id=uuid.uuid4(),
                    student_id=uuid.uuid4(),
                    starts_at=datetime(2026, 7, 22, 9, 0, tzinfo=UTC),
                    ends_at=datetime(2026, 7, 22, 10, 0, tzinfo=UTC),
                    classroom="B2",
                ),
            ],
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    previous = os.environ.get("JWT_SECRET")
    os.environ["JWT_SECRET"] = SECRET
    app = create_app()

    def _override() -> AdminKpiService:
        return _FakeAdminKpiService()  # type: ignore[return-value]

    app.dependency_overrides[get_admin_kpi_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    if previous is None:
        os.environ.pop("JWT_SECRET", None)
    else:
        os.environ["JWT_SECRET"] = previous


def _header(role: Role) -> dict[str, str]:
    token = JwtTokenService(
        secret=SECRET,
        access_expire_minutes=15,
        refresh_expire_days=7,
    ).create_access_token(
        AccessTokenClaims(
            user_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            email=f"{role.value}@example.com",
            role=role.value,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def test_admin_kpis_ok_for_admin(client: TestClient) -> None:
    response = client.get("/api/v1/admin/kpis", headers=_header(Role.ADMIN))
    assert response.status_code == 200
    body = response.json()
    assert body["student_count"] == 10
    assert body["unpaid_invoice_count"] == 3
    assert body["revenue_by_period"][0]["period"] == "2026-S1"
    assert len(body["today_schedules"]) == 1
