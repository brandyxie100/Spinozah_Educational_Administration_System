"""Student and enrolment domain entities.

Teacher lives in ``app.domain.students.teacher`` (same bounded context).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4


class EnrolmentStatus(StrEnum):
    """Lifecycle state of a lesson package enrolment."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Enrolment:
    """Lesson package for a student; tracks total vs completed lessons."""

    student_id: UUID
    tenant_id: UUID
    total_lessons: int
    completed_lessons: int = 0
    status: EnrolmentStatus = EnrolmentStatus.ACTIVE
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Validate lesson counts on construction."""
        if self.total_lessons < 0:
            raise ValueError("total_lessons must be non-negative")
        if self.completed_lessons < 0:
            raise ValueError("completed_lessons must be non-negative")
        if self.completed_lessons > self.total_lessons:
            raise ValueError("completed_lessons cannot exceed total_lessons")

    def remaining_lessons(self) -> int:
        """Return lessons still available on this enrolment."""
        return self.total_lessons - self.completed_lessons

    def complete_lesson(self) -> None:
        """Consume one lesson; mark completed when balance reaches zero."""
        if self.status != EnrolmentStatus.ACTIVE:
            raise ValueError("Only active enrolments can complete lessons")
        if self.remaining_lessons() <= 0:
            raise ValueError("No remaining lessons on this enrolment")
        self.completed_lessons += 1
        if self.remaining_lessons() == 0:
            self.status = EnrolmentStatus.COMPLETED


@dataclass(slots=True)
class Student:
    """Learner profile belonging to a single tenant."""

    tenant_id: UUID
    full_name: str
    email: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Require a non-empty display name."""
        if not self.full_name.strip():
            raise ValueError("full_name must not be empty")

    def deactivate(self) -> None:
        """Soft-deactivate the student profile."""
        self.is_active = False
