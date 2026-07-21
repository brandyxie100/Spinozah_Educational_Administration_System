"""Application service for teacher CRUD."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.infrastructure.persistence.teacher_models import TeacherModel
from app.infrastructure.persistence.teacher_repository import (
    SqlAlchemyTeacherRepository,
)
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository


class TeacherNotFoundError(Exception):
    """Raised when a tenant-scoped teacher id does not exist."""


class TeacherEmailConflictError(Exception):
    """Raised when email is already used within the tenant."""


class TeacherUserLinkError(Exception):
    """Raised when optional user_id cannot be linked (missing or taken)."""


@dataclass(frozen=True, slots=True)
class TeacherPage:
    """Paginated teacher listing."""

    items: list[TeacherModel]
    total: int
    page: int
    page_size: int


class TeacherService:
    """Create, read, update, and delete teachers for one tenant."""

    def __init__(
        self,
        repository: SqlAlchemyTeacherRepository,
        user_repository: SqlAlchemyUserRepository,
    ) -> None:
        """Bind tenant-scoped teacher and user repositories."""
        self._repository = repository
        self._user_repository = user_repository

    async def list_teachers(self, *, page: int, page_size: int) -> TeacherPage:
        """Return a page of teachers for the bound tenant."""
        items, total = await self._repository.list_paginated(
            page=page,
            page_size=page_size,
        )
        return TeacherPage(items=items, total=total, page=page, page_size=page_size)

    async def get_teacher(self, teacher_id: UUID) -> TeacherModel:
        """Load one teacher or raise if missing in this tenant."""
        teacher = await self._repository.get_by_id(teacher_id)
        if teacher is None:
            raise TeacherNotFoundError(f"Teacher not found: {teacher_id}")
        return teacher

    async def _ensure_email_available(
        self,
        email: str | None,
        *,
        exclude_teacher_id: UUID | None = None,
    ) -> None:
        if email is None:
            return
        existing = await self._repository.get_by_email(email)
        if existing is not None and existing.id != exclude_teacher_id:
            raise TeacherEmailConflictError(f"Email already registered: {email}")

    async def _ensure_user_linkable(
        self,
        user_id: UUID | None,
        *,
        exclude_teacher_id: UUID | None = None,
    ) -> None:
        """Validate optional user_id exists in tenant and is not already linked."""
        if user_id is None:
            return
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise TeacherUserLinkError(f"User not found in tenant: {user_id}")
        linked = await self._repository.get_by_user_id(user_id)
        if linked is not None and linked.id != exclude_teacher_id:
            raise TeacherUserLinkError(f"User already linked to a teacher: {user_id}")

    async def create_teacher(
        self,
        *,
        full_name: str,
        email: str | None,
        user_id: UUID | None = None,
    ) -> TeacherModel:
        """Create a teacher in the bound tenant; optionally link a user."""
        await self._ensure_email_available(email)
        await self._ensure_user_linkable(user_id)
        name = full_name.strip()
        if not name:
            raise ValueError("full_name must not be empty")
        teacher = TeacherModel(
            tenant_id=self._repository.tenant_id,
            full_name=name,
            email=email,
            user_id=user_id,
            is_active=True,
        )
        return await self._repository.add(teacher)

    async def update_teacher(
        self,
        teacher_id: UUID,
        *,
        full_name: str,
        email: str | None,
        is_active: bool,
        user_id: UUID | None,
    ) -> TeacherModel:
        """Replace mutable fields for a teacher (PUT semantics)."""
        teacher = await self.get_teacher(teacher_id)
        await self._ensure_email_available(email, exclude_teacher_id=teacher_id)
        await self._ensure_user_linkable(user_id, exclude_teacher_id=teacher_id)
        name = full_name.strip()
        if not name:
            raise ValueError("full_name must not be empty")
        teacher.full_name = name
        teacher.email = email
        teacher.is_active = is_active
        teacher.user_id = user_id
        return await self._repository.save(teacher)

    async def delete_teacher(self, teacher_id: UUID) -> None:
        """Hard-delete a teacher in the bound tenant."""
        teacher = await self.get_teacher(teacher_id)
        await self._repository.delete(teacher)
