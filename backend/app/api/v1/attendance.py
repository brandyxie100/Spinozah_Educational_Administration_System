"""Attendance check-in, teacher confirmation, and leave approval endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.attendance_schemas import (
    AttendanceCheckInRequest,
    AttendanceConfirmRequest,
    AttendanceOut,
    LeaveRequestCreate,
    LeaveRequestOut,
)
from app.application.attendance.attendance_service import (
    AttendanceConflictError,
    AttendanceNotFoundError,
    AttendanceResult,
    AttendanceService,
    ConfirmOutcome,
    EnrolmentNotFoundError,
    ScheduleNotFoundForAttendanceError,
)
from app.application.attendance.leave_service import (
    LeaveEnrolmentNotFoundError,
    LeaveNotFoundError,
    LeaveService,
    LeaveStudentNotFoundError,
)
from app.domain.attendance.leave_policy import LeaveKind, LeaveRequest
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyAttendanceRepository,
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.leave_repository import (
    SqlAlchemyLeaveRequestRepository,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])


def get_attendance_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK, Role.TEACHER)),
    ],
) -> AttendanceService:
    """Compose attendance service scoped to the caller's tenant."""
    return AttendanceService(
        attendance_repository=SqlAlchemyAttendanceRepository(
            session,
            claims.tenant_id,
        ),
        enrolment_repository=SqlAlchemyEnrolmentRepository(
            session,
            claims.tenant_id,
        ),
        schedule_repository=SqlAlchemyScheduleRepository(session, claims.tenant_id),
    )


def get_leave_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
) -> LeaveService:
    """Compose leave service for frontdesk request/approval workflow."""
    return LeaveService(
        leave_repository=SqlAlchemyLeaveRequestRepository(session, claims.tenant_id),
        enrolment_repository=SqlAlchemyEnrolmentRepository(session, claims.tenant_id),
        student_repository=SqlAlchemyStudentRepository(session, claims.tenant_id),
    )


def _to_out(result: AttendanceResult) -> AttendanceOut:
    record = result.attendance
    return AttendanceOut(
        id=record.id,
        tenant_id=record.tenant_id,
        schedule_id=record.schedule_id,
        student_id=record.student_id,
        enrolment_id=record.enrolment_id,
        status=record.status.value,
        remaining_lessons=result.remaining_lessons,
    )


def _to_leave_out(leave: LeaveRequest) -> LeaveRequestOut:
    return LeaveRequestOut(
        id=leave.id,
        tenant_id=leave.tenant_id,
        student_id=leave.student_id,
        enrolment_id=leave.enrolment_id,
        leave_date=leave.leave_date,
        kind=leave.kind.value,
        reason=leave.reason,
        status=leave.status.value,
        is_free=leave.is_free,
        extension_days_applied=leave.extension_days_applied,
    )


@router.post(
    "/check-in",
    response_model=AttendanceOut,
    status_code=status.HTTP_201_CREATED,
)
async def check_in(
    body: AttendanceCheckInRequest,
    service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> AttendanceOut:
    """Create a pending attendance check-in awaiting teacher confirmation."""
    try:
        result = await service.check_in(
            schedule_id=body.schedule_id,
            enrolment_id=body.enrolment_id,
        )
    except ScheduleNotFoundForAttendanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EnrolmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except AttendanceConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return _to_out(result)


@router.post(
    "/leave-requests",
    response_model=LeaveRequestOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_leave_request(
    body: LeaveRequestCreate,
    service: Annotated[LeaveService, Depends(get_leave_service)],
) -> LeaveRequestOut:
    """Submit a leave request pending frontdesk approval."""
    try:
        leave = await service.request_leave(
            student_id=body.student_id,
            leave_date=body.leave_date,
            kind=LeaveKind(body.kind),
            reason=body.reason,
            enrolment_id=body.enrolment_id,
        )
    except LeaveStudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except LeaveEnrolmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _to_leave_out(leave)


@router.post(
    "/leave-requests/{leave_id}/approve",
    response_model=LeaveRequestOut,
)
async def approve_leave_request(
    leave_id: UUID,
    service: Annotated[LeaveService, Depends(get_leave_service)],
) -> LeaveRequestOut:
    """Frontdesk approves leave; applies free-leave / semester-extension policy."""
    try:
        leave = await service.approve_leave(leave_id)
    except LeaveNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except LeaveEnrolmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_leave_out(leave)


@router.post(
    "/leave-requests/{leave_id}/reject",
    response_model=LeaveRequestOut,
)
async def reject_leave_request(
    leave_id: UUID,
    service: Annotated[LeaveService, Depends(get_leave_service)],
) -> LeaveRequestOut:
    """Frontdesk rejects a pending leave request."""
    try:
        leave = await service.reject_leave(leave_id)
    except LeaveNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_leave_out(leave)


@router.post("/{attendance_id}/confirm", response_model=AttendanceOut)
async def confirm_attendance(
    attendance_id: UUID,
    body: AttendanceConfirmRequest,
    service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> AttendanceOut:
    """Teacher confirms present/absent; present decrements remaining lessons."""
    try:
        result = await service.confirm(
            attendance_id,
            outcome=ConfirmOutcome(body.outcome),
        )
    except AttendanceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EnrolmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_out(result)
