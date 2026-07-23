"""Staff APIs to persist and retrieve exam/essay analyses."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.analysis_schemas import AnalysisCreateRequest, AnalysisOut
from app.application.ai_analysis.analysis_service import (
    AnalysisNotFoundError,
    AnalysisService,
    AnalysisStudentNotFoundError,
)
from app.domain.ai_analysis.entities import AnalysisKind, AnalysisRecord
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.analysis_repository import (
    SqlAlchemyAnalysisRepository,
)
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)

router = APIRouter(prefix="/api/v1/analyses", tags=["analyses"])


def get_analysis_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK, Role.TEACHER)),
    ],
) -> AnalysisService:
    """Compose analysis service scoped to the caller's tenant."""
    return AnalysisService(
        analysis_repository=SqlAlchemyAnalysisRepository(
            session,
            claims.tenant_id,
        ),
        student_repository=SqlAlchemyStudentRepository(
            session,
            claims.tenant_id,
        ),
    )


def _to_out(record: AnalysisRecord) -> AnalysisOut:
    return AnalysisOut(
        id=record.id,
        tenant_id=record.tenant_id,
        kind=record.kind.value,
        student_id=record.student_id,
        student_name=record.student_name,
        title=record.title,
        payload=record.payload,
    )


@router.post("", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    body: AnalysisCreateRequest,
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
) -> AnalysisOut:
    """Persist an exam or essay analysis report."""
    try:
        record = await service.create_analysis(
            kind=body.kind,
            payload=body.payload,
            student_id=body.student_id,
        )
    except AnalysisStudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _to_out(record)


@router.get("", response_model=list[AnalysisOut])
async def list_analyses(
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
    kind: Annotated[AnalysisKind | None, Query()] = None,
    student_id: Annotated[UUID | None, Query()] = None,
) -> list[AnalysisOut]:
    """List analyses in the caller's tenant (optional filters)."""
    rows = await service.list_analyses(kind=kind, student_id=student_id)
    return [_to_out(row) for row in rows]


@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: UUID,
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
) -> AnalysisOut:
    """Fetch one analysis by id within the caller's tenant."""
    try:
        record = await service.get_analysis(analysis_id)
    except AnalysisNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _to_out(record)
