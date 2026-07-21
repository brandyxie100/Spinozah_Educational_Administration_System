"""Domain unit tests for attendance confirmation and lesson consumption."""

from __future__ import annotations

import uuid

import pytest
from app.domain.attendance import AttendanceRecord, AttendanceStatus
from app.domain.students import Enrolment


def _enrolment(*, completed: int = 0, total: int = 10) -> Enrolment:
    return Enrolment(
        student_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        total_lessons=total,
        completed_lessons=completed,
    )


def test_confirm_present_decrements_remaining_lessons() -> None:
    enrolment = _enrolment(completed=2, total=10)
    record = AttendanceRecord(
        tenant_id=enrolment.tenant_id,
        schedule_id=uuid.uuid4(),
        student_id=enrolment.student_id,
        enrolment_id=enrolment.id,
    )
    record.confirm_present(enrolment)
    assert record.status == AttendanceStatus.PRESENT
    assert enrolment.completed_lessons == 3
    assert enrolment.remaining_lessons() == 7


def test_confirm_absent_does_not_consume_lesson() -> None:
    enrolment = _enrolment(completed=2, total=10)
    record = AttendanceRecord(
        tenant_id=enrolment.tenant_id,
        schedule_id=uuid.uuid4(),
        student_id=enrolment.student_id,
        enrolment_id=enrolment.id,
    )
    record.confirm_absent()
    assert record.status == AttendanceStatus.ABSENT
    assert enrolment.completed_lessons == 2


def test_confirm_present_rejects_non_pending() -> None:
    enrolment = _enrolment()
    record = AttendanceRecord(
        tenant_id=enrolment.tenant_id,
        schedule_id=uuid.uuid4(),
        student_id=enrolment.student_id,
        enrolment_id=enrolment.id,
        status=AttendanceStatus.PRESENT,
    )
    with pytest.raises(ValueError, match="pending"):
        record.confirm_present(enrolment)
