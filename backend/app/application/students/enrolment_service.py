"""Application service for staff enrolment management."""

from __future__ import annotations

from uuid import UUID

from app.domain.students.entities import Enrolment, EnrolmentStatus
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)


class EnrolmentNotFoundError(Exception):
    """Raised when a tenant-scoped enrolment id does not exist."""


class EnrolmentStudentNotFoundError(Exception):
    """Raised when create references an unknown student in the tenant."""


class EnrolmentService:
    """Create, list, and update lesson-package enrolments for one tenant."""

    def __init__(
        self,
        enrolment_repository: SqlAlchemyEnrolmentRepository,
        student_repository: SqlAlchemyStudentRepository,
    ) -> None:
        """Bind tenant-scoped enrolment and student repositories."""
        self._enrolments = enrolment_repository
        self._students = student_repository

    async def list_enrolments(
        self,
        *,
        student_id: UUID | None = None,
    ) -> list[Enrolment]:
        """List enrolments, optionally filtered by student."""
        if student_id is not None:
            return await self._enrolments.list_by_student_id(student_id)
        return await self._enrolments.list_all()

    async def get_enrolment(self, enrolment_id: UUID) -> Enrolment:
        """Load one enrolment or raise if missing in this tenant."""
        enrolment = await self._enrolments.get_by_id(enrolment_id)
        if enrolment is None:
            raise EnrolmentNotFoundError(f"Enrolment not found: {enrolment_id}")
        return enrolment

    async def create_enrolment(
        self,
        *,
        student_id: UUID,
        total_lessons: int,
    ) -> Enrolment:
        """Create an active enrolment package for a student."""
        student = await self._students.get_by_id(student_id)
        if student is None:
            raise EnrolmentStudentNotFoundError(
                f"Student not found: {student_id}",
            )
        enrolment = Enrolment(
            tenant_id=self._students.tenant_id,
            student_id=student_id,
            total_lessons=total_lessons,
            completed_lessons=0,
            status=EnrolmentStatus.ACTIVE,
        )
        return await self._enrolments.add(enrolment)

    async def update_enrolment(
        self,
        enrolment_id: UUID,
        *,
        total_lessons: int | None = None,
        completed_lessons: int | None = None,
        remaining_lessons: int | None = None,
        status: EnrolmentStatus | None = None,
    ) -> Enrolment:
        """Update lesson counts and/or status for an enrolment.

        When ``remaining_lessons`` is set, ``total_lessons`` becomes
        ``completed_lessons + remaining_lessons`` (using the updated completed
        count when provided).
        """
        enrolment = await self.get_enrolment(enrolment_id)

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

        # Reconstruct via entity validation (raises ValueError on bad counts).
        updated = Enrolment(
            id=enrolment.id,
            tenant_id=enrolment.tenant_id,
            student_id=enrolment.student_id,
            total_lessons=next_total,
            completed_lessons=next_completed,
            extension_days=enrolment.extension_days,
            status=status if status is not None else enrolment.status,
        )
        return await self._enrolments.save(updated)
