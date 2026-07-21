"""Application service for admin user management."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.identity.passwords import PasswordHasher
from app.domain.identity.roles import Role
from app.infrastructure.persistence.models import UserModel, UserRole
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository


class UserNotFoundError(Exception):
    """Raised when a tenant-scoped user id does not exist."""


class UserEmailConflictError(Exception):
    """Raised when email is already used within the tenant."""


@dataclass(frozen=True, slots=True)
class UserPage:
    """Paginated user listing."""

    items: list[UserModel]
    total: int
    page: int
    page_size: int


class UserManagementService:
    """Create, list, update, and deactivate users for one tenant."""

    def __init__(
        self,
        repository: SqlAlchemyUserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        """Bind tenant-scoped repository and password hasher."""
        self._repository = repository
        self._password_hasher = password_hasher

    async def list_users(self, *, page: int, page_size: int) -> UserPage:
        """Return a page of users for the bound tenant."""
        items, total = await self._repository.list_users_paginated(
            page=page,
            page_size=page_size,
        )
        return UserPage(items=items, total=total, page=page, page_size=page_size)

    async def create_user(
        self,
        *,
        email: str,
        full_name: str,
        password: str,
        role: Role,
    ) -> UserModel:
        """Create a user in the bound tenant."""
        existing = await self._repository.get_by_email(email)
        if existing is not None:
            raise UserEmailConflictError(f"Email already registered: {email}")
        user = UserModel(
            tenant_id=self._repository.tenant_id,
            email=email,
            full_name=full_name,
            hashed_password=self._password_hasher.hash(password),
            role=UserRole(role.value),
            is_active=True,
        )
        return await self._repository.add(user)

    async def update_user(
        self,
        user_id: UUID,
        *,
        full_name: str | None = None,
        role: Role | None = None,
        password: str | None = None,
    ) -> UserModel:
        """Update mutable fields for a user in the bound tenant."""
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User not found: {user_id}")
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = UserRole(role.value)
        if password is not None:
            user.hashed_password = self._password_hasher.hash(password)
        return await self._repository.save(user)

    async def deactivate_user(self, user_id: UUID) -> UserModel:
        """Soft-deactivate a user (sets is_active=False)."""
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User not found: {user_id}")
        user.is_active = False
        return await self._repository.save(user)
