"""Parent portal magic-link auth and linked-student endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_token_service, require_roles
from app.api.v1.auth import _set_refresh_cookie, _to_token_response
from app.api.v1.auth_schemas import TokenResponse
from app.api.v1.parent_schemas import (
    LinkedStudentOut,
    MagicLinkConsumeRequest,
    MagicLinkRequest,
    MagicLinkRequestResponse,
    ParentStudentLinkCreate,
    ParentStudentLinkOut,
)
from app.application.parent_portal.magic_link_service import (
    NotAParentError,
    ParentNotFoundError,
    ParentPortalService,
    StudentNotFoundError,
)
from app.core.settings import Settings, get_settings
from app.domain.identity.exceptions import InvalidCredentialsError
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.email.magic_link_mailer import LoggingMagicLinkMailer
from app.infrastructure.persistence.session import get_session
from app.infrastructure.security.jwt_token_service import JwtTokenService

router = APIRouter(prefix="/api/v1/parent", tags=["parent-portal"])


def get_parent_portal_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[JwtTokenService, Depends(get_token_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ParentPortalService:
    """Compose parent portal service for public magic-link endpoints."""
    return ParentPortalService(
        session=session,
        token_service=token_service,
        mailer=LoggingMagicLinkMailer(),
        magic_link_ttl_minutes=settings.magic_link_expire_minutes,
        magic_link_base_url=settings.magic_link_base_url,
        expose_magic_url=settings.debug,
    )


@router.post(
    "/magic-link/request",
    response_model=MagicLinkRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_magic_link(
    body: MagicLinkRequest,
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> MagicLinkRequestResponse:
    """Email a one-time magic link for parent login (anti-enumeration)."""
    result = await service.request_magic_link(
        tenant_slug=body.tenant_slug,
        email=str(body.email),
    )
    return MagicLinkRequestResponse(magic_url=result.magic_url)


@router.post("/magic-link/consume", response_model=TokenResponse)
async def consume_magic_link(
    body: MagicLinkConsumeRequest,
    response: Response,
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    """Exchange a magic-link token for access JWT + refresh cookie."""
    try:
        tokens = await service.consume_magic_link(raw_token=body.token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    _set_refresh_cookie(response, tokens.refresh_token, settings)
    return _to_token_response(tokens)


@router.post(
    "/student-links",
    response_model=ParentStudentLinkOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_student_link(
    body: ParentStudentLinkCreate,
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.ADMIN, Role.FRONTDESK)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> ParentStudentLinkOut:
    """Link a parent user to a student (required for portal scoping)."""
    try:
        link = await service.link_student(
            tenant_id=claims.tenant_id,
            parent_user_id=body.parent_user_id,
            student_id=body.student_id,
        )
    except ParentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except StudentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except NotAParentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return ParentStudentLinkOut(
        id=link.id,
        tenant_id=link.tenant_id,
        parent_user_id=link.parent_user_id,
        student_id=link.student_id,
    )


@router.get("/students", response_model=list[LinkedStudentOut])
async def list_linked_students(
    claims: Annotated[
        AccessTokenClaims,
        Depends(require_roles(Role.PARENT)),
    ],
    service: Annotated[ParentPortalService, Depends(get_parent_portal_service)],
) -> list[LinkedStudentOut]:
    """Return students linked to the authenticated parent only."""
    rows = await service.list_linked_students(
        tenant_id=claims.tenant_id,
        parent_user_id=claims.user_id,
    )
    return [
        LinkedStudentOut(
            id=row.id,
            full_name=row.full_name,
            email=row.email,
            is_active=row.is_active,
        )
        for row in rows
    ]
