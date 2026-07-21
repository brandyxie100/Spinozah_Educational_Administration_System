"""Schedule HTTP endpoints with conflict detection (409)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.schedule_schemas import (
    ScheduleConflictOut,
    ScheduleCreateRequest,
    ScheduleOut,
)
from app.application.scheduling.schedule_service import (
    ScheduleConflictError,
    ScheduleService,
)
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.domain.scheduling.conflict_detection import ConflictDetectionService
from app.domain.scheduling.entities import Schedule
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from app.infrastructure.persistence.session import get_session

router = APIRouter(prefix="/api/v1/schedules", tags=["schedules"])


def get_schedule_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
) -> ScheduleService:
    """Compose schedule service scoped to the caller's tenant."""
    repository = SqlAlchemyScheduleRepository(session, claims.tenant_id)
    return ScheduleService(
        repository=repository,
        conflict_detector=ConflictDetectionService(),
    )


def _to_schedule_out(schedule: Schedule) -> ScheduleOut:
    recurrence = schedule.recurrence
    return ScheduleOut(
        id=schedule.id,
        tenant_id=schedule.tenant_id,
        teacher_id=schedule.teacher_id,
        student_id=schedule.student_id,
        classroom=schedule.classroom,
        starts_at=schedule.starts_at,
        ends_at=schedule.ends_at,
        status=schedule.status.value,
        is_recurring=schedule.is_recurring,
        recurrence_weekday=int(recurrence.weekday) if recurrence else None,
        recurrence_until=recurrence.until if recurrence else None,
    )


@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    body: ScheduleCreateRequest,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> ScheduleOut:
    """Create a schedule; returns 409 when teacher/student/classroom overlap."""
    try:
        schedule = await service.create_schedule(
            teacher_id=body.teacher_id,
            student_id=body.student_id,
            starts_at=body.starts_at,
            ends_at=body.ends_at,
            classroom=body.classroom,
            is_recurring=body.is_recurring,
            recurrence_until=body.recurrence_until,
        )
    except ScheduleConflictError as exc:
        detail = [
            ScheduleConflictOut(
                kind=conflict.kind.value,
                existing_schedule_id=conflict.existing_schedule_id,
                proposed_starts_at=conflict.proposed_slot.starts_at,
                proposed_ends_at=conflict.proposed_slot.ends_at,
                existing_starts_at=conflict.existing_slot.starts_at,
                existing_ends_at=conflict.existing_slot.ends_at,
            ).model_dump(mode="json")
            for conflict in exc.conflicts
        ]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_schedule_out(schedule)
