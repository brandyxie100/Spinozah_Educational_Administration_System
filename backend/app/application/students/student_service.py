"""Application service for student CRUD."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.infrastructure.persistence.student_models import StudentModel
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)


class StudentNotFoundError(Exception):
    """Raised when a tenant-scoped student id does not exist."""


class StudentEmailConflictError(Exception):
    """Raised when email is already used within the tenant."""


@dataclass(frozen=True, slots=True)
class StudentPage:
    """Paginated student listing."""

    items: list[StudentModel]
    total: int
    page: int
    page_size: int


class StudentService:
    """Create, read, update, and delete students for one tenant."""

    def __init__(self, repository: SqlAlchemyStudentRepository) -> None:
        """Bind a tenant-scoped student repository."""
        self._repository = repository

    async def list_students(self, *, page: int, page_size: int) -> StudentPage:
        """Return a page of students for the bound tenant."""
        items, total = await self._repository.list_paginated(
            page=page,
            page_size=page_size,
        )
        return StudentPage(items=items, total=total, page=page, page_size=page_size)

    async def get_student(self, student_id: UUID) -> StudentModel:
        """Load one student or raise if missing in this tenant."""
        student = await self._repository.get_by_id(student_id)
        if student is None:
            raise StudentNotFoundError(f"Student not found: {student_id}")
        return student

    async def create_student(
        self,
        *,
        full_name: str,
        email: str | None,
    ) -> StudentModel:
        """Create a student in the bound tenant."""
        if email is not None:
            existing = await self._repository.get_by_email(email)
            if existing is not None:
                raise StudentEmailConflictError(f"Email already registered: {email}")
        student = StudentModel(
            tenant_id=self._repository.tenant_id,
            full_name=full_name.strip(),
            email=email,
            is_active=True,
        )
        if not student.full_name:
            raise ValueError("full_name must not be empty")
        return await self._repository.add(student)

    async def update_student(
        self,
        student_id: UUID,
        *,
        full_name: str,
        email: str | None,
        is_active: bool,
    ) -> StudentModel:
        """Replace mutable fields for a student (PUT semantics)."""
        student = await self.get_student(student_id)
        if email is not None:
            existing = await self._repository.get_by_email(email)
            if existing is not None and existing.id != student_id:
                raise StudentEmailConflictError(f"Email already registered: {email}")
        name = full_name.strip()
        if not name:
            raise ValueError("full_name must not be empty")
        student.full_name = name
        student.email = email
        student.is_active = is_active
        return await self._repository.save(student)

    async def delete_student(self, student_id: UUID) -> None:
        """Hard-delete a student in the bound tenant."""
        student = await self.get_student(student_id)
        await self._repository.delete(student)
