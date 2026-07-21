"""Unit tests for schedule create route conflict → HTTP 409."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from app.api.v1.schedules import get_schedule_service
from app.application.scheduling.schedule_service import (
    ScheduleConflictError,
    ScheduleService,
)
from app.domain.scheduling.conflict_detection import (
    ConflictKind,
    ScheduleConflict,
)
from app.domain.scheduling.entities import Schedule, TimeSlot
from app.main import create_app
from fastapi.testclient import TestClient

TZ = UTC


class _FakeScheduleService:
    def __init__(self, *, conflict: bool = False) -> None:
        self.conflict = conflict
        self.tenant_id = uuid.uuid4()

    async def create_schedule(self, **kwargs: object) -> Schedule:
        if self.conflict:
            proposed = TimeSlot(
                datetime(2026, 10, 14, 16, 0, tzinfo=TZ),
                datetime(2026, 10, 14, 17, 0, tzinfo=TZ),
            )
            raise ScheduleConflictError(
                [
                    ScheduleConflict(
                        kind=ConflictKind.TEACHER,
                        existing_schedule_id=uuid.uuid4(),
                        proposed_slot=proposed,
                        existing_slot=proposed,
                    ),
                ],
            )
        return Schedule(
            tenant_id=self.tenant_id,
            teacher_id=kwargs["teacher_id"],  # type: ignore[arg-type]
            student_id=kwargs["student_id"],  # type: ignore[arg-type]
            starts_at=kwargs["starts_at"],  # type: ignore[arg-type]
            ends_at=kwargs["ends_at"],  # type: ignore[arg-type]
            classroom=kwargs.get("classroom"),  # type: ignore[arg-type]
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeScheduleService()
    app = create_app()

    def _override() -> ScheduleService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_schedule_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def conflict_client() -> Iterator[TestClient]:
    fake = _FakeScheduleService(conflict=True)
    app = create_app()

    def _override() -> ScheduleService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_schedule_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _payload() -> dict[str, object]:
    return {
        "teacher_id": str(uuid.uuid4()),
        "student_id": str(uuid.uuid4()),
        "starts_at": "2026-10-14T16:00:00Z",
        "ends_at": "2026-10-14T17:00:00Z",
        "classroom": "Room A",
        "is_recurring": False,
    }


def test_create_schedule_returns_201(client: TestClient) -> None:
    response = client.post("/api/v1/schedules", json=_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "not_started"
    assert body["is_recurring"] is False


def test_create_schedule_returns_409_on_conflict(
    conflict_client: TestClient,
) -> None:
    response = conflict_client.post("/api/v1/schedules", json=_payload())
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert detail[0]["kind"] == "teacher"
