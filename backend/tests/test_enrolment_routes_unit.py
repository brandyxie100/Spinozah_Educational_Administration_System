"""Unit tests for enrolment management routes (dependency overrides, no DB)."""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from app.api.v1.enrolments import get_enrolment_service
from app.application.students.enrolment_service import (
    EnrolmentNotFoundError,
    EnrolmentService,
    EnrolmentStudentNotFoundError,
)
from app.domain.students.entities import Enrolment, EnrolmentStatus
from app.main import create_app
from fastapi.testclient import TestClient


class _FakeEnrolmentService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self._rows: dict[uuid.UUID, Enrolment] = {}

    async def list_enrolments(
        self,
        *,
        student_id: uuid.UUID | None = None,
    ) -> list[Enrolment]:
        rows = list(self._rows.values())
        if student_id is not None:
            rows = [row for row in rows if row.student_id == student_id]
        return rows

    async def create_enrolment(
        self,
        *,
        student_id: uuid.UUID,
        total_lessons: int,
    ) -> Enrolment:
        if student_id.hex.startswith("dead"):
            raise EnrolmentStudentNotFoundError(f"Student not found: {student_id}")
        enrolment = Enrolment(
            tenant_id=self.tenant_id,
            student_id=student_id,
            total_lessons=total_lessons,
        )
        self._rows[enrolment.id] = enrolment
        return enrolment

    async def update_enrolment(
        self,
        enrolment_id: uuid.UUID,
        *,
        total_lessons: int | None = None,
        completed_lessons: int | None = None,
        remaining_lessons: int | None = None,
        status: EnrolmentStatus | None = None,
    ) -> Enrolment:
        enrolment = self._rows.get(enrolment_id)
        if enrolment is None:
            raise EnrolmentNotFoundError(f"Enrolment not found: {enrolment_id}")
        next_completed = (
            completed_lessons
            if completed_lessons is not None
            else enrolment.completed_lessons
        )
        if remaining_lessons is not None:
            next_total = next_completed + remaining_lessons
        elif total_lessons is not None:
            next_total = total_lessons
        else:
            next_total = enrolment.total_lessons
        updated = Enrolment(
            id=enrolment.id,
            tenant_id=enrolment.tenant_id,
            student_id=enrolment.student_id,
            total_lessons=next_total,
            completed_lessons=next_completed,
            extension_days=enrolment.extension_days,
            status=status if status is not None else enrolment.status,
        )
        self._rows[enrolment.id] = updated
        return updated


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeEnrolmentService()
    app = create_app()

    def _override() -> EnrolmentService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_enrolment_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_enrolment_create_list_update_flow(client: TestClient) -> None:
    student_id = str(uuid.uuid4())
    created = client.post(
        "/api/v1/enrolments",
        json={"student_id": student_id, "total_lessons": 12},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["remaining_lessons"] == 12
    enrolment_id = body["id"]

    listed = client.get(f"/api/v1/enrolments?student_id={student_id}")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.patch(
        f"/api/v1/enrolments/{enrolment_id}",
        json={"remaining_lessons": 8},
    )
    assert updated.status_code == 200
    assert updated.json()["remaining_lessons"] == 8
    assert updated.json()["total_lessons"] == 8


def test_create_unknown_student_returns_404(client: TestClient) -> None:
    # Fake service treats ids starting with "dead" as missing.
    student_id = "dead0000-0000-4000-8000-000000000001"
    response = client.post(
        "/api/v1/enrolments",
        json={"student_id": student_id, "total_lessons": 5},
    )
    assert response.status_code == 404
