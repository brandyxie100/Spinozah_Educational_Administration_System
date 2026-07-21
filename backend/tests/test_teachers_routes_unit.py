"""Unit tests for teacher CRUD routes (dependency overrides, no DB)."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from app.api.v1.teachers import get_teacher_service
from app.application.students.teacher_service import (
    TeacherNotFoundError,
    TeacherPage,
    TeacherService,
)
from app.main import create_app
from fastapi.testclient import TestClient


@dataclass
class _FakeTeacher:
    id: uuid.UUID
    tenant_id: uuid.UUID
    full_name: str
    email: str | None
    user_id: uuid.UUID | None = None
    is_active: bool = True


class _FakeTeacherService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self.teachers: dict[uuid.UUID, _FakeTeacher] = {}

    async def list_teachers(self, *, page: int, page_size: int) -> TeacherPage:
        items = list(self.teachers.values())
        start = (page - 1) * page_size
        return TeacherPage(
            items=items[start : start + page_size],  # type: ignore[arg-type]
            total=len(items),
            page=page,
            page_size=page_size,
        )

    async def get_teacher(self, teacher_id: uuid.UUID) -> _FakeTeacher:
        teacher = self.teachers.get(teacher_id)
        if teacher is None:
            raise TeacherNotFoundError(f"Teacher not found: {teacher_id}")
        return teacher

    async def create_teacher(
        self,
        *,
        full_name: str,
        email: str | None,
        user_id: uuid.UUID | None = None,
    ) -> _FakeTeacher:
        teacher = _FakeTeacher(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            full_name=full_name,
            email=email,
            user_id=user_id,
        )
        self.teachers[teacher.id] = teacher
        return teacher

    async def update_teacher(
        self,
        teacher_id: uuid.UUID,
        *,
        full_name: str,
        email: str | None,
        is_active: bool,
        user_id: uuid.UUID | None,
    ) -> _FakeTeacher:
        teacher = await self.get_teacher(teacher_id)
        teacher.full_name = full_name
        teacher.email = email
        teacher.is_active = is_active
        teacher.user_id = user_id
        return teacher

    async def delete_teacher(self, teacher_id: uuid.UUID) -> None:
        await self.get_teacher(teacher_id)
        del self.teachers[teacher_id]


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeTeacherService()
    app = create_app()

    def _override() -> TeacherService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_teacher_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_teacher_crud_post_get_put_delete(client: TestClient) -> None:
    created = client.post(
        "/api/v1/teachers",
        json={"full_name": "Alex Teacher", "email": "alex-t@example.com"},
    )
    assert created.status_code == 201
    assert created.json()["user_id"] is None
    teacher_id = created.json()["id"]

    listed = client.get("/api/v1/teachers?page=1&page_size=10")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    fetched = client.get(f"/api/v1/teachers/{teacher_id}")
    assert fetched.status_code == 200
    assert fetched.json()["full_name"] == "Alex Teacher"

    updated = client.put(
        f"/api/v1/teachers/{teacher_id}",
        json={
            "full_name": "Alex Updated",
            "email": "alex-t@example.com",
            "is_active": True,
            "user_id": None,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Alex Updated"

    deleted = client.delete(f"/api/v1/teachers/{teacher_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/teachers/{teacher_id}").status_code == 404
