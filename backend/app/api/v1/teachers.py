"""Teacher CRUD HTTP endpoints."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.schedule_schemas import (
    TeacherScheduleResponse,
    TeacherScheduleSlotOut,
)
from app.api.v1.teacher_schemas import (
    TeacherCreateRequest,
    TeacherListResponse,
    TeacherOut,
    TeacherUpdateRequest,
)
from app.application.scheduling.schedule_service import (
    ScheduleService,
    TeacherNotFoundForScheduleError,
)
from app.application.students.teacher_service import (
    TeacherEmailConflictError,
    TeacherNotFoundError,
    TeacherService,
    TeacherUserLinkError,
)
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.domain.scheduling.conflict_detection import ConflictDetectionService
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)
from app.infrastructure.persistence.teacher_models import TeacherModel
from app.infrastructure.persistence.teacher_repository import (
    SqlAlchemyTeacherRepository,
)
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository

router = APIRouter(prefix="/api/v1/teachers", tags=["teachers"])


def get_teacher_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
) -> TeacherService:
    """Compose teacher service scoped to the caller's tenant."""
    repository = SqlAlchemyTeacherRepository(session, claims.tenant_id)
    user_repository = SqlAlchemyUserRepository(session, claims.tenant_id)
    return TeacherService(repository=repository, user_repository=user_repository)


def get_teacher_schedule_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK, Role.TEACHER)),
    ],
) -> ScheduleService:
    """Compose schedule service for teacher timetable reads."""
    return ScheduleService(
        repository=SqlAlchemyScheduleRepository(session, claims.tenant_id),
        conflict_detector=ConflictDetectionService(),
        teacher_repository=SqlAlchemyTeacherRepository(session, claims.tenant_id),
        student_repository=SqlAlchemyStudentRepository(session, claims.tenant_id),
    )


def _to_teacher_out(teacher: TeacherModel) -> TeacherOut:
    return TeacherOut(
        id=teacher.id,
        tenant_id=teacher.tenant_id,
        full_name=teacher.full_name,
        email=teacher.email,
        user_id=teacher.user_id,
        is_active=teacher.is_active,
    )


@router.get("", response_model=TeacherListResponse)
async def list_teachers(
    service: Annotated[TeacherService, Depends(get_teacher_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TeacherListResponse:
    """List teachers in the caller's tenant with pagination."""
    result = await service.list_teachers(page=page, page_size=page_size)
    return TeacherListResponse(
        items=[_to_teacher_out(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.post("", response_model=TeacherOut, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    body: TeacherCreateRequest,
    service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherOut:
    """Create a teacher in the caller's tenant."""
    try:
        teacher = await service.create_teacher(
            full_name=body.full_name,
            email=body.email,
            user_id=body.user_id,
        )
    except TeacherEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except TeacherUserLinkError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_teacher_out(teacher)


@router.get("/{teacher_id}/schedule", response_model=TeacherScheduleResponse)
async def get_teacher_schedule(
    teacher_id: UUID,
    service: Annotated[ScheduleService, Depends(get_teacher_schedule_service)],
    range_start: Annotated[date, Query()],
    range_end: Annotated[date, Query()],
) -> TeacherScheduleResponse:
    """Return expanded daily/weekly slots for a teacher."""
    try:
        items = await service.get_teacher_schedule(
            teacher_id,
            range_start=range_start,
            range_end=range_end,
        )
    except TeacherNotFoundForScheduleError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return TeacherScheduleResponse(
        teacher_id=teacher_id,
        range_start=range_start,
        range_end=range_end,
        items=[
            TeacherScheduleSlotOut(
                schedule_id=item.schedule_id,
                student_id=item.student_id,
                student_name=item.student_name,
                classroom=item.classroom,
                starts_at=item.starts_at,
                ends_at=item.ends_at,
                status=item.status,
                display_status=item.display_status.value,
            )
            for item in items
        ],
    )


@router.get("/{teacher_id}", response_model=TeacherOut)
async def get_teacher(
    teacher_id: UUID,
    service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherOut:
    """Fetch one teacher by id within the caller's tenant."""
    try:
        teacher = await service.get_teacher(teacher_id)
    except TeacherNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _to_teacher_out(teacher)


@router.put("/{teacher_id}", response_model=TeacherOut)
async def update_teacher(
    teacher_id: UUID,
    body: TeacherUpdateRequest,
    service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherOut:
    """Replace teacher fields (PUT) within the caller's tenant."""
    try:
        teacher = await service.update_teacher(
            teacher_id,
            full_name=body.full_name,
            email=body.email,
            is_active=body.is_active,
            user_id=body.user_id,
        )
    except TeacherNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except TeacherEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except TeacherUserLinkError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_teacher_out(teacher)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: UUID,
    service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> None:
    """Delete a teacher within the caller's tenant."""
    try:
        await service.delete_teacher(teacher_id)
    except TeacherNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
