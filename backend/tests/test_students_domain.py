"""Domain unit tests for Student and Enrolment."""

from __future__ import annotations

import uuid

import pytest
from app.domain.students import Enrolment, EnrolmentStatus, Student


def test_enrolment_remaining_lessons_total_minus_completed() -> None:
    """Remaining lessons equals total − completed."""
    enrolment = Enrolment(
        student_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        total_lessons=10,
        completed_lessons=3,
    )
    assert enrolment.remaining_lessons() == 7


def test_enrolment_rejects_completed_exceeding_total() -> None:
    """Construction fails when completed_lessons > total_lessons."""
    with pytest.raises(ValueError, match="cannot exceed"):
        Enrolment(
            student_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            total_lessons=5,
            completed_lessons=6,
        )


def test_enrolment_complete_lesson_updates_balance_and_status() -> None:
    """Completing the last lesson marks enrolment completed."""
    enrolment = Enrolment(
        student_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        total_lessons=1,
        completed_lessons=0,
    )
    enrolment.complete_lesson()
    assert enrolment.completed_lessons == 1
    assert enrolment.remaining_lessons() == 0
    assert enrolment.status == EnrolmentStatus.COMPLETED


def test_enrolment_complete_lesson_with_no_balance_raises() -> None:
    """Cannot complete a lesson when none remain."""
    enrolment = Enrolment(
        student_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        total_lessons=1,
        completed_lessons=1,
        status=EnrolmentStatus.COMPLETED,
    )
    with pytest.raises(ValueError, match="Only active|No remaining"):
        enrolment.complete_lesson()


def test_student_requires_non_empty_full_name() -> None:
    """Student full_name cannot be blank."""
    with pytest.raises(ValueError, match="full_name"):
        Student(tenant_id=uuid.uuid4(), full_name="   ")


def test_student_deactivate_sets_inactive() -> None:
    """deactivate() flips is_active to False."""
    student = Student(tenant_id=uuid.uuid4(), full_name="Alex Student")
    student.deactivate()
    assert student.is_active is False
