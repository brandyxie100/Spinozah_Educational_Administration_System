"""Unit tests for attendance check-in / confirm routes."""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from app.api.v1.attendance import get_attendance_service
from app.application.attendance.attendance_service import (
    AttendanceResult,
    AttendanceService,
    ConfirmOutcome,
)
from app.domain.attendance import AttendanceRecord, AttendanceStatus
from app.main import create_app
from fastapi.testclient import TestClient


class _FakeAttendanceService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self._records: dict[uuid.UUID, AttendanceRecord] = {}
        self._remaining = 9

    async def check_in(
        self,
        *,
        schedule_id: uuid.UUID,
        enrolment_id: uuid.UUID | None = None,
    ) -> AttendanceResult:
        record = AttendanceRecord(
            tenant_id=self.tenant_id,
            schedule_id=schedule_id,
            student_id=uuid.uuid4(),
            enrolment_id=enrolment_id or uuid.uuid4(),
        )
        self._records[record.id] = record
        return AttendanceResult(attendance=record, remaining_lessons=self._remaining)

    async def confirm(
        self,
        attendance_id: uuid.UUID,
        *,
        outcome: ConfirmOutcome,
    ) -> AttendanceResult:
        record = self._records[attendance_id]
        if outcome == ConfirmOutcome.PRESENT:
            record.status = AttendanceStatus.PRESENT
            self._remaining -= 1
        else:
            record.status = AttendanceStatus.ABSENT
        return AttendanceResult(attendance=record, remaining_lessons=self._remaining)

    async def list_attendance(
        self,
        *,
        status: str | None = None,
        student_id: uuid.UUID | None = None,
        limit: int = 100,
    ) -> list[AttendanceResult]:
        rows = list(self._records.values())
        if student_id is not None:
            rows = [row for row in rows if row.student_id == student_id]
        if status is not None:
            rows = [row for row in rows if row.status.value == status]
        return [
            AttendanceResult(attendance=row, remaining_lessons=self._remaining)
            for row in rows[:limit]
        ]


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeAttendanceService()
    app = create_app()

    def _override() -> AttendanceService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_attendance_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_check_in_and_confirm_present_flow(client: TestClient) -> None:
    schedule_id = str(uuid.uuid4())
    created = client.post(
        "/api/v1/attendance/check-in",
        json={"schedule_id": schedule_id},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "pending_confirmation"
    assert body["remaining_lessons"] == 9
    attendance_id = body["id"]

    confirmed = client.post(
        f"/api/v1/attendance/{attendance_id}/confirm",
        json={"outcome": "present"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "present"
    assert confirmed.json()["remaining_lessons"] == 8


def test_list_attendance_returns_checked_in_rows(client: TestClient) -> None:
    schedule_id = str(uuid.uuid4())
    created = client.post(
        "/api/v1/attendance/check-in",
        json={"schedule_id": schedule_id},
    )
    assert created.status_code == 201

    listed = client.get("/api/v1/attendance?status=pending_confirmation")
    assert listed.status_code == 200
    body = listed.json()
    assert len(body) == 1
    assert body[0]["status"] == "pending_confirmation"
