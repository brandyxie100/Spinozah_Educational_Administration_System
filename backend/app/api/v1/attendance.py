"""Attendance check-in and teacher confirmation HTTP endpoints."""

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
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyAttendanceRepository,
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from app.infrastructure.persistence.session import get_session

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
