"""Unit tests for leave request approval routes."""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from app.api.v1.attendance import get_leave_service
from app.application.attendance.leave_service import LeaveService
from app.domain.attendance import LeaveRequest, LeaveStatus
from app.main import create_app
from fastapi.testclient import TestClient


class _FakeLeaveService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self._rows: dict[uuid.UUID, LeaveRequest] = {}

    async def request_leave(self, **kwargs: object) -> LeaveRequest:
        leave = LeaveRequest(
            tenant_id=self.tenant_id,
            student_id=kwargs["student_id"],  # type: ignore[arg-type]
            enrolment_id=kwargs.get("enrolment_id") or uuid.uuid4(),  # type: ignore[arg-type]
            leave_date=kwargs["leave_date"],  # type: ignore[arg-type]
            kind=kwargs["kind"],  # type: ignore[arg-type]
            reason=kwargs.get("reason"),  # type: ignore[arg-type]
        )
        self._rows[leave.id] = leave
        return leave

    async def approve_leave(self, leave_id: uuid.UUID) -> LeaveRequest:
        leave = self._rows[leave_id]
        leave.status = LeaveStatus.APPROVED
        leave.is_free = True
        leave.extension_days_applied = 0
        return leave

    async def reject_leave(self, leave_id: uuid.UUID) -> LeaveRequest:
        leave = self._rows[leave_id]
        leave.status = LeaveStatus.REJECTED
        return leave


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeLeaveService()
    app = create_app()

    def _override() -> LeaveService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_leave_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_leave_request_and_approve_flow(client: TestClient) -> None:
    created = client.post(
        "/api/v1/attendance/leave-requests",
        json={
            "student_id": str(uuid.uuid4()),
            "leave_date": "2026-11-12",
            "kind": "sick",
            "reason": "Fever",
        },
    )
    assert created.status_code == 201
    leave_id = created.json()["id"]
    assert created.json()["status"] == "pending"

    approved = client.post(f"/api/v1/attendance/leave-requests/{leave_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["is_free"] is True
