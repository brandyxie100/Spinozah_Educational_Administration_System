"""Domain unit tests for leave policy and leave request approval."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from app.domain.attendance import (
    EXTENSION_DAYS_PER_EXTRA_LEAVE,
    FREE_LEAVES_PER_TERM,
    LeaveKind,
    LeavePolicyEngine,
    LeaveRequest,
    LeaveStatus,
)
from app.domain.students import Enrolment


def _enrolment() -> Enrolment:
    return Enrolment(
        student_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        total_lessons=20,
        completed_lessons=0,
    )


def test_first_two_leaves_are_free() -> None:
    engine = LeavePolicyEngine()
    assert FREE_LEAVES_PER_TERM == 2
    first = engine.decide(0)
    second = engine.decide(1)
    assert first.is_free is True and first.extension_days == 0
    assert second.is_free is True and second.extension_days == 0


def test_third_leave_extends_semester() -> None:
    engine = LeavePolicyEngine()
    third = engine.decide(2)
    assert third.is_free is False
    assert third.extension_days == EXTENSION_DAYS_PER_EXTRA_LEAVE


def test_approve_free_leave_does_not_extend_enrolment() -> None:
    enrolment = _enrolment()
    leave = LeaveRequest(
        tenant_id=enrolment.tenant_id,
        student_id=enrolment.student_id,
        enrolment_id=enrolment.id,
        leave_date=date(2026, 11, 12),
        kind=LeaveKind.SICK,
    )
    leave.approve(LeavePolicyEngine().decide(0), enrolment)
    assert leave.status == LeaveStatus.APPROVED
    assert leave.is_free is True
    assert leave.extension_days_applied == 0
    assert enrolment.extension_days == 0


def test_approve_extra_leave_extends_enrolment() -> None:
    enrolment = _enrolment()
    leave = LeaveRequest(
        tenant_id=enrolment.tenant_id,
        student_id=enrolment.student_id,
        enrolment_id=enrolment.id,
        leave_date=date(2026, 11, 12),
        kind=LeaveKind.PERSONAL,
    )
    leave.approve(LeavePolicyEngine().decide(2), enrolment)
    assert leave.is_free is False
    assert leave.extension_days_applied == EXTENSION_DAYS_PER_EXTRA_LEAVE
    assert enrolment.extension_days == EXTENSION_DAYS_PER_EXTRA_LEAVE


def test_reject_pending_leave() -> None:
    enrolment = _enrolment()
    leave = LeaveRequest(
        tenant_id=enrolment.tenant_id,
        student_id=enrolment.student_id,
        enrolment_id=enrolment.id,
        leave_date=date(2026, 11, 12),
        kind=LeaveKind.SICK,
    )
    leave.reject()
    assert leave.status == LeaveStatus.REJECTED
    with pytest.raises(ValueError, match="pending"):
        leave.approve(LeavePolicyEngine().decide(0), enrolment)
