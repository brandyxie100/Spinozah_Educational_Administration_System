"""Unit tests for LeaveService free-leave policy workflow."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

import pytest
from app.application.attendance.leave_service import LeaveService
from app.domain.attendance import (
    EXTENSION_DAYS_PER_EXTRA_LEAVE,
    LeaveKind,
    LeaveRequest,
    LeaveStatus,
)
from app.domain.students import Enrolment
from app.infrastructure.persistence.student_models import StudentModel


class _MemoryLeaveRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, LeaveRequest] = {}

    async def get_by_id(self, leave_id: uuid.UUID) -> LeaveRequest | None:
        return self._rows.get(leave_id)

    async def count_approved_for_enrolment(self, enrolment_id: uuid.UUID) -> int:
        return sum(
            1
            for row in self._rows.values()
            if row.enrolment_id == enrolment_id and row.status == LeaveStatus.APPROVED
        )

    async def add(self, leave: LeaveRequest) -> LeaveRequest:
        self._rows[leave.id] = leave
        return leave

    async def save(self, leave: LeaveRequest) -> LeaveRequest:
        self._rows[leave.id] = leave
        return leave


class _MemoryEnrolmentRepo:
    def __init__(self, enrolment: Enrolment) -> None:
        self._enrolment = enrolment

    async def get_by_id(self, enrolment_id: uuid.UUID) -> Enrolment | None:
        if self._enrolment.id == enrolment_id:
            return self._enrolment
        return None

    async def get_active_for_student(self, student_id: uuid.UUID) -> Enrolment | None:
        if self._enrolment.student_id == student_id:
            return self._enrolment
        return None

    async def save(self, enrolment: Enrolment) -> Enrolment:
        self._enrolment = enrolment
        return enrolment


class _MemoryStudentRepo:
    def __init__(self, student: StudentModel) -> None:
        self._student = student

    async def get_by_id(self, student_id: uuid.UUID) -> StudentModel | None:
        if self._student.id == student_id:
            return self._student
        return None


@pytest.mark.asyncio
async def test_leave_service_third_approval_extends_semester() -> None:
    tenant_id = uuid.uuid4()
    student_id = uuid.uuid4()
    enrolment = Enrolment(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        total_lessons=20,
        completed_lessons=0,
    )
    student = StudentModel(
        id=student_id,
        tenant_id=tenant_id,
        full_name="Charlotte",
        email=None,
        is_active=True,
    )
    leave_repo: Any = _MemoryLeaveRepo(tenant_id)
    service = LeaveService(
        leave_repository=leave_repo,
        enrolment_repository=_MemoryEnrolmentRepo(enrolment),  # type: ignore[arg-type]
        student_repository=_MemoryStudentRepo(student),  # type: ignore[arg-type]
    )

    for index in range(3):
        leave = await service.request_leave(
            student_id=student_id,
            leave_date=date(2026, 11, 10 + index),
            kind=LeaveKind.SICK,
        )
        approved = await service.approve_leave(leave.id)
        if index < 2:
            assert approved.is_free is True
            assert approved.extension_days_applied == 0
        else:
            assert approved.is_free is False
            assert approved.extension_days_applied == EXTENSION_DAYS_PER_EXTRA_LEAVE

    assert enrolment.extension_days == EXTENSION_DAYS_PER_EXTRA_LEAVE
