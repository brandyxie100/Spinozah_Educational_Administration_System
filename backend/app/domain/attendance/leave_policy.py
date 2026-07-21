"""Leave request entity and free-leave policy engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.students.entities import Enrolment

# First N approved leaves in a term do not extend the semester.
FREE_LEAVES_PER_TERM = 2
# Each additional approved leave extends the course by one calendar week.
EXTENSION_DAYS_PER_EXTRA_LEAVE = 7


class LeaveKind(StrEnum):
    """Supported leave categories."""

    SICK = "sick"
    PERSONAL = "personal"


class LeaveStatus(StrEnum):
    """Leave request approval workflow states."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class LeavePolicyDecision:
    """Outcome of applying the free-leave policy for one approval."""

    is_free: bool
    extension_days: int


class LeavePolicyEngine:
    """Decide free vs semester-extending leave from prior approvals this term."""

    def decide(self, approved_leaves_this_term: int) -> LeavePolicyDecision:
        """Return policy decision before counting the leave being approved.

        Args:
            approved_leaves_this_term: Already-approved leaves on the enrolment.
        """
        if approved_leaves_this_term < 0:
            raise ValueError("approved_leaves_this_term must be non-negative")
        if approved_leaves_this_term < FREE_LEAVES_PER_TERM:
            return LeavePolicyDecision(is_free=True, extension_days=0)
        return LeavePolicyDecision(
            is_free=False,
            extension_days=EXTENSION_DAYS_PER_EXTRA_LEAVE,
        )


@dataclass(slots=True)
class LeaveRequest:
    """Student leave request awaiting (or past) frontdesk approval."""

    tenant_id: UUID
    student_id: UUID
    enrolment_id: UUID
    leave_date: date
    kind: LeaveKind
    reason: str | None = None
    status: LeaveStatus = LeaveStatus.PENDING
    is_free: bool | None = None
    extension_days_applied: int = 0
    id: UUID = field(default_factory=uuid4)

    def approve(
        self,
        decision: LeavePolicyDecision,
        enrolment: Enrolment,
    ) -> None:
        """Frontdesk approves leave and applies semester extension if needed."""
        if self.status != LeaveStatus.PENDING:
            raise ValueError("Only pending leave requests can be approved")
        if enrolment.id != self.enrolment_id:
            raise ValueError("Enrolment does not match this leave request")
        if enrolment.student_id != self.student_id:
            raise ValueError("Enrolment student does not match leave request")

        self.status = LeaveStatus.APPROVED
        self.is_free = decision.is_free
        self.extension_days_applied = decision.extension_days
        if decision.extension_days > 0:
            enrolment.extend_semester(decision.extension_days)

    def reject(self) -> None:
        """Frontdesk rejects a pending leave request."""
        if self.status != LeaveStatus.PENDING:
            raise ValueError("Only pending leave requests can be rejected")
        self.status = LeaveStatus.REJECTED
        self.is_free = None
        self.extension_days_applied = 0
