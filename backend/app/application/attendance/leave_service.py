"""Application service for leave requests and free-leave policy."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from app.domain.attendance.leave_policy import (
    LeaveKind,
    LeavePolicyEngine,
    LeaveRequest,
    LeaveStatus,
)
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.leave_repository import (
    SqlAlchemyLeaveRequestRepository,
)
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)


class LeaveNotFoundError(Exception):
    """Raised when a leave request id is missing in the tenant."""


class LeaveEnrolmentNotFoundError(Exception):
    """Raised when no suitable enrolment exists for the leave."""


class LeaveStudentNotFoundError(Exception):
    """Raised when the student id is missing in the tenant."""


class LeaveService:
    """Create leave requests and run frontdesk approval with policy engine."""

    def __init__(
        self,
        leave_repository: SqlAlchemyLeaveRequestRepository,
        enrolment_repository: SqlAlchemyEnrolmentRepository,
        student_repository: SqlAlchemyStudentRepository,
        policy_engine: LeavePolicyEngine | None = None,
    ) -> None:
        """Bind repositories and optional policy engine."""
        self._leaves = leave_repository
        self._enrolments = enrolment_repository
        self._students = student_repository
        self._policy = policy_engine or LeavePolicyEngine()

    async def request_leave(
        self,
        *,
        student_id: UUID,
        leave_date: date,
        kind: LeaveKind,
        reason: str | None = None,
        enrolment_id: UUID | None = None,
    ) -> LeaveRequest:
        """Create a pending leave request for frontdesk approval."""
        student = await self._students.get_by_id(student_id)
        if student is None:
            raise LeaveStudentNotFoundError(f"Student not found: {student_id}")

        if enrolment_id is not None:
            enrolment = await self._enrolments.get_by_id(enrolment_id)
        else:
            enrolment = await self._enrolments.get_active_for_student(student_id)
        if enrolment is None:
            raise LeaveEnrolmentNotFoundError(
                f"No active enrolment for student: {student_id}",
            )
        if enrolment.student_id != student_id:
            raise LeaveEnrolmentNotFoundError(
                "Enrolment does not belong to the student",
            )

        leave = LeaveRequest(
            tenant_id=self._leaves.tenant_id,
            student_id=student_id,
            enrolment_id=enrolment.id,
            leave_date=leave_date,
            kind=kind,
            reason=reason,
            status=LeaveStatus.PENDING,
        )
        return await self._leaves.add(leave)

    async def approve_leave(self, leave_id: UUID) -> LeaveRequest:
        """Approve leave; first two per term are free, extras extend semester."""
        leave = await self._leaves.get_by_id(leave_id)
        if leave is None:
            raise LeaveNotFoundError(f"Leave request not found: {leave_id}")

        enrolment = await self._enrolments.get_by_id(leave.enrolment_id)
        if enrolment is None:
            raise LeaveEnrolmentNotFoundError(
                f"Enrolment not found: {leave.enrolment_id}",
            )

        approved_count = await self._leaves.count_approved_for_enrolment(
            leave.enrolment_id,
        )
        decision = self._policy.decide(approved_count)
        leave.approve(decision, enrolment)
        await self._enrolments.save(enrolment)
        return await self._leaves.save(leave)

    async def reject_leave(self, leave_id: UUID) -> LeaveRequest:
        """Reject a pending leave request without policy side effects."""
        leave = await self._leaves.get_by_id(leave_id)
        if leave is None:
            raise LeaveNotFoundError(f"Leave request not found: {leave_id}")
        leave.reject()
        return await self._leaves.save(leave)
