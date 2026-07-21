"""Unit tests for StudentService with an in-memory repository double."""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from app.application.students.student_service import (
    StudentEmailConflictError,
    StudentNotFoundError,
    StudentService,
)
from app.infrastructure.persistence.student_models import StudentModel


class _MemoryStudentRepo:
    """Minimal async repository double for StudentService tests."""

    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, StudentModel] = {}

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[StudentModel], int]:
        items = list(self._rows.values())
        start = (page - 1) * page_size
        return items[start : start + page_size], len(items)

    async def get_by_id(self, student_id: uuid.UUID) -> StudentModel | None:
        return self._rows.get(student_id)

    async def get_by_email(self, email: str) -> StudentModel | None:
        for row in self._rows.values():
            if row.email == email:
                return row
        return None

    async def add(self, student: StudentModel) -> StudentModel:
        if student.id is None:
            student.id = uuid.uuid4()
        self._rows[student.id] = student
        return student

    async def save(self, student: StudentModel) -> StudentModel:
        self._rows[student.id] = student
        return student

    async def delete(self, student: StudentModel) -> None:
        self._rows.pop(student.id, None)


@pytest.fixture
def service() -> StudentService:
    repo: Any = _MemoryStudentRepo(uuid.uuid4())
    return StudentService(repository=repo)


@pytest.mark.asyncio
async def test_student_service_create_list_update_delete(
    service: StudentService,
) -> None:
    created = await service.create_student(
        full_name="Casey",
        email="casey@example.com",
    )
    page = await service.list_students(page=1, page_size=10)
    assert page.total == 1
    assert page.items[0].id == created.id

    updated = await service.update_student(
        created.id,
        full_name="Casey Updated",
        email="casey@example.com",
        is_active=False,
    )
    assert updated.full_name == "Casey Updated"
    assert updated.is_active is False

    await service.delete_student(created.id)
    with pytest.raises(StudentNotFoundError):
        await service.get_student(created.id)


@pytest.mark.asyncio
async def test_student_service_rejects_duplicate_email(
    service: StudentService,
) -> None:
    await service.create_student(full_name="One", email="dup@example.com")
    with pytest.raises(StudentEmailConflictError):
        await service.create_student(full_name="Two", email="dup@example.com")
