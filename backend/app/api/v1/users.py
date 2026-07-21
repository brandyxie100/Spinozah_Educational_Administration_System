"""Admin user management HTTP endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.api.v1.user_schemas import (
    UserCreateRequest,
    UserListResponse,
    UserOut,
    UserUpdateRequest,
)
from app.application.identity.user_service import (
    UserEmailConflictError,
    UserManagementService,
    UserNotFoundError,
)
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.models import UserModel
from app.infrastructure.persistence.session import get_session
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_user_management_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[AccessTokenClaims, Depends(require_roles(Role.ADMIN))],
) -> UserManagementService:
    """Compose admin user management scoped to the caller's tenant."""
    repository = SqlAlchemyUserRepository(session, claims.tenant_id)
    return UserManagementService(
        repository=repository,
        password_hasher=BcryptPasswordHasher(),
    )


def _to_user_out(user: UserModel) -> UserOut:
    return UserOut(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        full_name=user.full_name,
        role=Role(user.role.value),
        is_active=user.is_active,
    )


@router.get("", response_model=UserListResponse)
async def list_users(
    service: Annotated[UserManagementService, Depends(get_user_management_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> UserListResponse:
    """List users in the admin's tenant with pagination."""
    result = await service.list_users(page=page, page_size=page_size)
    return UserListResponse(
        items=[_to_user_out(user) for user in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreateRequest,
    service: Annotated[UserManagementService, Depends(get_user_management_service)],
) -> UserOut:
    """Create a user in the admin's tenant."""
    try:
        user = await service.create_user(
            email=body.email,
            full_name=body.full_name,
            password=body.password,
            role=body.role,
        )
    except UserEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return _to_user_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    body: UserUpdateRequest,
    service: Annotated[UserManagementService, Depends(get_user_management_service)],
) -> UserOut:
    """Update a user in the admin's tenant."""
    try:
        user = await service.update_user(
            user_id,
            full_name=body.full_name,
            role=body.role,
            password=body.password,
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _to_user_out(user)


@router.post("/{user_id}/deactivate", response_model=UserOut)
async def deactivate_user(
    user_id: UUID,
    service: Annotated[UserManagementService, Depends(get_user_management_service)],
) -> UserOut:
    """Deactivate a user (soft disable) in the admin's tenant."""
    try:
        user = await service.deactivate_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _to_user_out(user)
