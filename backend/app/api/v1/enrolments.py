"""Staff enrolment management HTTP endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.enrolment_schemas import (
    EnrolmentCreateRequest,
    EnrolmentOut,
    EnrolmentUpdateRequest,
)
from app.application.students.enrolment_service import (
    EnrolmentNotFoundError,
    EnrolmentService,
    EnrolmentStudentNotFoundError,
)
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.domain.students.entities import Enrolment
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)

router = APIRouter(prefix="/api/v1/enrolments", tags=["enrolments"])


def get_enrolment_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
) -> EnrolmentService:
    """Compose enrolment service scoped to the caller's tenant."""
    return EnrolmentService(
        enrolment_repository=SqlAlchemyEnrolmentRepository(
            session,
            claims.tenant_id,
        ),
        student_repository=SqlAlchemyStudentRepository(
            session,
            claims.tenant_id,
        ),
    )


def _to_enrolment_out(enrolment: Enrolment) -> EnrolmentOut:
    return EnrolmentOut(
        id=enrolment.id,
        tenant_id=enrolment.tenant_id,
        student_id=enrolment.student_id,
        total_lessons=enrolment.total_lessons,
        completed_lessons=enrolment.completed_lessons,
        remaining_lessons=enrolment.remaining_lessons(),
        extension_days=enrolment.extension_days,
        status=enrolment.status.value,
    )


@router.get("", response_model=list[EnrolmentOut])
async def list_enrolments(
    service: Annotated[EnrolmentService, Depends(get_enrolment_service)],
    student_id: Annotated[UUID | None, Query()] = None,
) -> list[EnrolmentOut]:
    """List enrolments in the caller's tenant (optional student filter)."""
    rows = await service.list_enrolments(student_id=student_id)
    return [_to_enrolment_out(row) for row in rows]


@router.post("", response_model=EnrolmentOut, status_code=status.HTTP_201_CREATED)
async def create_enrolment(
    body: EnrolmentCreateRequest,
    service: Annotated[EnrolmentService, Depends(get_enrolment_service)],
) -> EnrolmentOut:
    """Create a lesson package enrolment for a student."""
    try:
        enrolment = await service.create_enrolment(
            student_id=body.student_id,
            total_lessons=body.total_lessons,
        )
    except EnrolmentStudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_enrolment_out(enrolment)


@router.patch("/{enrolment_id}", response_model=EnrolmentOut)
async def update_enrolment(
    enrolment_id: UUID,
    body: EnrolmentUpdateRequest,
    service: Annotated[EnrolmentService, Depends(get_enrolment_service)],
) -> EnrolmentOut:
    """Update lesson counts and/or status for an enrolment."""
    try:
        enrolment = await service.update_enrolment(
            enrolment_id,
            total_lessons=body.total_lessons,
            completed_lessons=body.completed_lessons,
            remaining_lessons=body.remaining_lessons,
            status=body.status,
        )
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
    return _to_enrolment_out(enrolment)
