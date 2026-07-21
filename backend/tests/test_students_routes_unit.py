"""Unit tests for student CRUD routes (dependency overrides, no DB)."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from app.api.v1.students import get_student_service
from app.application.students.student_service import (
    StudentNotFoundError,
    StudentPage,
    StudentService,
)
from app.main import create_app
from fastapi.testclient import TestClient


@dataclass
class _FakeStudent:
    id: uuid.UUID
    tenant_id: uuid.UUID
    full_name: str
    email: str | None
    is_active: bool = True


class _FakeStudentService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self.students: dict[uuid.UUID, _FakeStudent] = {}

    async def list_students(self, *, page: int, page_size: int) -> StudentPage:
        items = list(self.students.values())
        start = (page - 1) * page_size
        return StudentPage(
            items=items[start : start + page_size],  # type: ignore[arg-type]
            total=len(items),
            page=page,
            page_size=page_size,
        )

    async def get_student(self, student_id: uuid.UUID) -> _FakeStudent:
        student = self.students.get(student_id)
        if student is None:
            raise StudentNotFoundError(f"Student not found: {student_id}")
        return student

    async def create_student(
        self,
        *,
        full_name: str,
        email: str | None,
    ) -> _FakeStudent:
        student = _FakeStudent(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            full_name=full_name,
            email=email,
        )
        self.students[student.id] = student
        return student

    async def update_student(
        self,
        student_id: uuid.UUID,
        *,
        full_name: str,
        email: str | None,
        is_active: bool,
    ) -> _FakeStudent:
        student = await self.get_student(student_id)
        student.full_name = full_name
        student.email = email
        student.is_active = is_active
        return student

    async def delete_student(self, student_id: uuid.UUID) -> None:
        await self.get_student(student_id)
        del self.students[student_id]


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeStudentService()
    app = create_app()

    def _override() -> StudentService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_student_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_student_crud_post_get_put_delete(client: TestClient) -> None:
    created = client.post(
        "/api/v1/students",
        json={"full_name": "Alex Student", "email": "alex@example.com"},
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    listed = client.get("/api/v1/students?page=1&page_size=10")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    fetched = client.get(f"/api/v1/students/{student_id}")
    assert fetched.status_code == 200
    assert fetched.json()["full_name"] == "Alex Student"

    updated = client.put(
        f"/api/v1/students/{student_id}",
        json={
            "full_name": "Alex Updated",
            "email": "alex@example.com",
            "is_active": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Alex Updated"

    deleted = client.delete(f"/api/v1/students/{student_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/students/{student_id}").status_code == 404
