"""Map leave request domain entities to ORM rows."""

from __future__ import annotations

from app.domain.attendance.leave_policy import LeaveKind, LeaveRequest, LeaveStatus
from app.infrastructure.persistence.leave_models import (
    LeaveKindDB,
    LeaveRequestModel,
    LeaveStatusDB,
)


def leave_to_model(leave: LeaveRequest) -> LeaveRequestModel:
    """Convert a domain leave request into a persistence model."""
    return LeaveRequestModel(
        id=leave.id,
        tenant_id=leave.tenant_id,
        student_id=leave.student_id,
        enrolment_id=leave.enrolment_id,
        leave_date=leave.leave_date,
        kind=LeaveKindDB(leave.kind.value),
        reason=leave.reason,
        status=LeaveStatusDB(leave.status.value),
        is_free=leave.is_free,
        extension_days_applied=leave.extension_days_applied,
    )


def model_to_leave(model: LeaveRequestModel) -> LeaveRequest:
    """Convert a persistence row into a domain leave request."""
    return LeaveRequest(
        id=model.id,
        tenant_id=model.tenant_id,
        student_id=model.student_id,
        enrolment_id=model.enrolment_id,
        leave_date=model.leave_date,
        kind=LeaveKind(model.kind.value),
        reason=model.reason,
        status=LeaveStatus(model.status.value),
        is_free=model.is_free,
        extension_days_applied=model.extension_days_applied,
    )
