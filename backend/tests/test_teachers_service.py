"""Unit tests for TeacherService with in-memory repository doubles."""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from app.application.students.teacher_service import (
    TeacherEmailConflictError,
    TeacherNotFoundError,
    TeacherService,
    TeacherUserLinkError,
)
from app.infrastructure.persistence.models import UserModel, UserRole
from app.infrastructure.persistence.teacher_models import TeacherModel


class _MemoryTeacherRepo:
    """Minimal async repository double for TeacherService tests."""

    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, TeacherModel] = {}

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[TeacherModel], int]:
        items = list(self._rows.values())
        start = (page - 1) * page_size
        return items[start : start + page_size], len(items)

    async def get_by_id(self, teacher_id: uuid.UUID) -> TeacherModel | None:
        return self._rows.get(teacher_id)

    async def get_by_email(self, email: str) -> TeacherModel | None:
        for row in self._rows.values():
            if row.email == email:
                return row
        return None

    async def get_by_user_id(self, user_id: uuid.UUID) -> TeacherModel | None:
        for row in self._rows.values():
            if row.user_id == user_id:
                return row
        return None

    async def add(self, teacher: TeacherModel) -> TeacherModel:
        if teacher.id is None:
            teacher.id = uuid.uuid4()
        self._rows[teacher.id] = teacher
        return teacher

    async def save(self, teacher: TeacherModel) -> TeacherModel:
        self._rows[teacher.id] = teacher
        return teacher

    async def delete(self, teacher: TeacherModel) -> None:
        self._rows.pop(teacher.id, None)


class _MemoryUserRepo:
    """Minimal user lookup double for optional teacher→user linking."""

    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, UserModel] = {}

    def seed(self, user: UserModel) -> None:
        self._rows[user.id] = user

    async def get_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        return self._rows.get(user_id)


@pytest.fixture
def service() -> TeacherService:
    tenant_id = uuid.uuid4()
    teachers: Any = _MemoryTeacherRepo(tenant_id)
    users: Any = _MemoryUserRepo(tenant_id)
    return TeacherService(repository=teachers, user_repository=users)


@pytest.mark.asyncio
async def test_teacher_service_create_list_update_delete(
    service: TeacherService,
) -> None:
    created = await service.create_teacher(
        full_name="Riley",
        email="riley@example.com",
    )
    page = await service.list_teachers(page=1, page_size=10)
    assert page.total == 1
    assert page.items[0].id == created.id
    assert created.user_id is None

    updated = await service.update_teacher(
        created.id,
        full_name="Riley Updated",
        email="riley@example.com",
        is_active=False,
        user_id=None,
    )
    assert updated.full_name == "Riley Updated"
    assert updated.is_active is False

    await service.delete_teacher(created.id)
    with pytest.raises(TeacherNotFoundError):
        await service.get_teacher(created.id)


@pytest.mark.asyncio
async def test_teacher_service_rejects_duplicate_email(
    service: TeacherService,
) -> None:
    await service.create_teacher(full_name="One", email="dup@example.com")
    with pytest.raises(TeacherEmailConflictError):
        await service.create_teacher(full_name="Two", email="dup@example.com")


@pytest.mark.asyncio
async def test_teacher_service_links_optional_user() -> None:
    tenant_id = uuid.uuid4()
    teachers: Any = _MemoryTeacherRepo(tenant_id)
    users: Any = _MemoryUserRepo(tenant_id)
    user = UserModel(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="login@example.com",
        full_name="Login User",
        hashed_password="x",
        role=UserRole.TEACHER,
        is_active=True,
    )
    users.seed(user)
    service = TeacherService(repository=teachers, user_repository=users)

    created = await service.create_teacher(
        full_name="Linked Teacher",
        email="linked@example.com",
        user_id=user.id,
    )
    assert created.user_id == user.id


@pytest.mark.asyncio
async def test_teacher_service_rejects_unknown_user_link(
    service: TeacherService,
) -> None:
    with pytest.raises(TeacherUserLinkError, match="User not found"):
        await service.create_teacher(
            full_name="Orphan",
            email="orphan@example.com",
            user_id=uuid.uuid4(),
        )
