"""Unit tests for EnrolmentService with in-memory repository doubles."""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from app.application.students.enrolment_service import (
    EnrolmentNotFoundError,
    EnrolmentService,
    EnrolmentStudentNotFoundError,
)
from app.domain.students.entities import Enrolment, EnrolmentStatus
from app.infrastructure.persistence.student_models import StudentModel


class _MemoryStudentRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, StudentModel] = {}

    async def get_by_id(self, student_id: uuid.UUID) -> StudentModel | None:
        return self._rows.get(student_id)

    def seed(self, student: StudentModel) -> None:
        self._rows[student.id] = student


class _MemoryEnrolmentRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, Enrolment] = {}

    async def list_by_student_id(self, student_id: uuid.UUID) -> list[Enrolment]:
        return [
            row for row in self._rows.values() if row.student_id == student_id
        ]

    async def list_all(self) -> list[Enrolment]:
        return list(self._rows.values())

    async def get_by_id(self, enrolment_id: uuid.UUID) -> Enrolment | None:
        return self._rows.get(enrolment_id)

    async def add(self, enrolment: Enrolment) -> Enrolment:
        self._rows[enrolment.id] = enrolment
        return enrolment

    async def save(self, enrolment: Enrolment) -> Enrolment:
        self._rows[enrolment.id] = enrolment
        return enrolment


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def service(tenant_id: uuid.UUID) -> tuple[EnrolmentService, _MemoryStudentRepo]:
    students: Any = _MemoryStudentRepo(tenant_id)
    enrolments: Any = _MemoryEnrolmentRepo(tenant_id)
    return EnrolmentService(enrolments, students), students


@pytest.mark.asyncio
async def test_create_list_and_update_remaining_lessons(
    service: tuple[EnrolmentService, _MemoryStudentRepo],
    tenant_id: uuid.UUID,
) -> None:
    enrolment_service, students = service
    student = StudentModel(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        full_name="Casey",
        email=None,
        is_active=True,
    )
    students.seed(student)

    created = await enrolment_service.create_enrolment(
        student_id=student.id,
        total_lessons=20,
    )
    assert created.remaining_lessons() == 20

    listed = await enrolment_service.list_enrolments(student_id=student.id)
    assert len(listed) == 1

    updated = await enrolment_service.update_enrolment(
        created.id,
        remaining_lessons=15,
    )
    assert updated.total_lessons == 15
    assert updated.completed_lessons == 0
    assert updated.remaining_lessons() == 15


@pytest.mark.asyncio
async def test_create_rejects_unknown_student(
    service: tuple[EnrolmentService, _MemoryStudentRepo],
) -> None:
    enrolment_service, _students = service
    with pytest.raises(EnrolmentStudentNotFoundError):
        await enrolment_service.create_enrolment(
            student_id=uuid.uuid4(),
            total_lessons=10,
        )


@pytest.mark.asyncio
async def test_update_rejects_missing_enrolment(
    service: tuple[EnrolmentService, _MemoryStudentRepo],
) -> None:
    enrolment_service, _students = service
    with pytest.raises(EnrolmentNotFoundError):
        await enrolment_service.update_enrolment(
            uuid.uuid4(),
            status=EnrolmentStatus.CANCELLED,
        )
