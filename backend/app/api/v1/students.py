"""Student CRUD HTTP endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.student_schemas import (
    StudentCreateRequest,
    StudentListResponse,
    StudentOut,
    StudentUpdateRequest,
)
from app.application.students.student_service import (
    StudentEmailConflictError,
    StudentNotFoundError,
    StudentService,
)
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.student_models import StudentModel
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)

router = APIRouter(prefix="/api/v1/students", tags=["students"])


def get_student_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
) -> StudentService:
    """Compose student service scoped to the caller's tenant."""
    repository = SqlAlchemyStudentRepository(session, claims.tenant_id)
    return StudentService(repository=repository)


def _to_student_out(student: StudentModel) -> StudentOut:
    return StudentOut(
        id=student.id,
        tenant_id=student.tenant_id,
        full_name=student.full_name,
        email=student.email,
        is_active=student.is_active,
    )


@router.get("", response_model=StudentListResponse)
async def list_students(
    service: Annotated[StudentService, Depends(get_student_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> StudentListResponse:
    """List students in the caller's tenant with pagination."""
    result = await service.list_students(page=page, page_size=page_size)
    return StudentListResponse(
        items=[_to_student_out(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(
    body: StudentCreateRequest,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> StudentOut:
    """Create a student in the caller's tenant."""
    try:
        student = await service.create_student(
            full_name=body.full_name,
            email=body.email,
        )
    except StudentEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_student_out(student)


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(
    student_id: UUID,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> StudentOut:
    """Fetch one student by id within the caller's tenant."""
    try:
        student = await service.get_student(student_id)
    except StudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _to_student_out(student)


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: UUID,
    body: StudentUpdateRequest,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> StudentOut:
    """Replace student fields (PUT) within the caller's tenant."""
    try:
        student = await service.update_student(
            student_id,
            full_name=body.full_name,
            email=body.email,
            is_active=body.is_active,
        )
    except StudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except StudentEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_student_out(student)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: UUID,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> None:
    """Delete a student within the caller's tenant."""
    try:
        await service.delete_student(student_id)
    except StudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
