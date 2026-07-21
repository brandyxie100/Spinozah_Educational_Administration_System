"""Unit tests for GET /teachers/{id}/schedule route."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime

import pytest
from app.api.v1.teachers import get_teacher_schedule_service
from app.application.scheduling.schedule_service import (
    ScheduleService,
    TeacherNotFoundForScheduleError,
    TeacherScheduleSlot,
)
from app.domain.scheduling.display_status import DisplayStatus
from app.main import create_app
from fastapi.testclient import TestClient

TZ = UTC


class _FakeScheduleService:
    def __init__(self, *, missing: bool = False) -> None:
        self.missing = missing

    async def get_teacher_schedule(
        self,
        teacher_id: uuid.UUID,
        *,
        range_start: date,
        range_end: date,
        now: datetime | None = None,
    ) -> list[TeacherScheduleSlot]:
        if self.missing:
            raise TeacherNotFoundForScheduleError(f"Teacher not found: {teacher_id}")
        return [
            TeacherScheduleSlot(
                schedule_id=uuid.uuid4(),
                student_id=uuid.uuid4(),
                student_name="Charlotte",
                classroom="Room A",
                starts_at=datetime(2026, 10, 14, 16, 0, tzinfo=TZ),
                ends_at=datetime(2026, 10, 14, 17, 0, tzinfo=TZ),
                status="not_started",
                display_status=DisplayStatus.STARTING_SOON,
            ),
            TeacherScheduleSlot(
                schedule_id=uuid.uuid4(),
                student_id=uuid.uuid4(),
                student_name="Chace",
                classroom=None,
                starts_at=datetime(2026, 10, 14, 17, 0, tzinfo=TZ),
                ends_at=datetime(2026, 10, 14, 18, 0, tzinfo=TZ),
                status="cancelled",
                display_status=DisplayStatus.ABSENT,
            ),
        ]


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeScheduleService()
    app = create_app()

    def _override() -> ScheduleService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_teacher_schedule_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_teacher_schedule_returns_slots(client: TestClient) -> None:
    teacher_id = uuid.uuid4()
    response = client.get(
        f"/api/v1/teachers/{teacher_id}/schedule"
        "?range_start=2026-10-14&range_end=2026-10-14",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["teacher_id"] == str(teacher_id)
    assert len(body["items"]) == 2
    statuses = {item["display_status"] for item in body["items"]}
    assert "starting_soon" in statuses
    assert "absent" in statuses
