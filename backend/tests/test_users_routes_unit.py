"""Unit tests for admin user CRUD routes (dependency overrides, no DB)."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from app.api.v1.users import get_user_management_service
from app.application.identity.user_service import (
    UserEmailConflictError,
    UserManagementService,
    UserNotFoundError,
    UserPage,
)
from app.domain.identity.roles import Role
from app.infrastructure.persistence.models import UserModel, UserRole
from app.main import create_app
from fastapi.testclient import TestClient


@dataclass
class _FakeUser:
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    hashed_password: str = "hashed"
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)


class _FakeUserService:
    """In-memory stand-in for UserManagementService."""

    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self.users: dict[uuid.UUID, _FakeUser] = {}

    async def list_users(self, *, page: int, page_size: int) -> UserPage:
        items = list(self.users.values())
        start = (page - 1) * page_size
        page_items = items[start : start + page_size]
        return UserPage(
            items=page_items,  # type: ignore[arg-type]
            total=len(items),
            page=page,
            page_size=page_size,
        )

    async def create_user(
        self,
        *,
        email: str,
        full_name: str,
        password: str,
        role: Role,
    ) -> UserModel:
        if any(user.email == email for user in self.users.values()):
            raise UserEmailConflictError(f"Email already registered: {email}")
        user = _FakeUser(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            email=email,
            full_name=full_name,
            role=UserRole(role.value),
            is_active=True,
        )
        self.users[user.id] = user
        return user  # type: ignore[return-value]

    async def update_user(
        self,
        user_id: uuid.UUID,
        *,
        full_name: str | None = None,
        role: Role | None = None,
        password: str | None = None,
    ) -> UserModel:
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User not found: {user_id}")
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = UserRole(role.value)
        return user  # type: ignore[return-value]

    async def deactivate_user(self, user_id: uuid.UUID) -> UserModel:
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User not found: {user_id}")
        user.is_active = False
        return user  # type: ignore[return-value]


@pytest.fixture
def fake_service() -> _FakeUserService:
    return _FakeUserService()


@pytest.fixture
def client(fake_service: _FakeUserService) -> Iterator[TestClient]:
    app = create_app()

    def _override() -> UserManagementService:
        return fake_service  # type: ignore[return-value]

    app.dependency_overrides[get_user_management_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_user_returns_201(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "email": "teacher@example.com",
            "full_name": "Pat Teacher",
            "password": "password12",
            "role": "teacher",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "teacher@example.com"
    assert payload["role"] == "teacher"
    assert payload["is_active"] is True


def test_list_users_returns_pagination(client: TestClient) -> None:
    client.post(
        "/api/v1/users",
        json={
            "email": "a@example.com",
            "full_name": "A",
            "password": "password12",
            "role": "admin",
        },
    )
    response = client.get("/api/v1/users?page=1&page_size=10")
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 10
    assert payload["total"] == 1
    assert len(payload["items"]) == 1


def test_update_and_deactivate_user(client: TestClient) -> None:
    created = client.post(
        "/api/v1/users",
        json={
            "email": "b@example.com",
            "full_name": "Before",
            "password": "password12",
            "role": "frontdesk",
        },
    ).json()
    user_id = created["id"]

    updated = client.patch(
        f"/api/v1/users/{user_id}",
        json={"full_name": "After", "role": "teacher"},
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "After"
    assert updated.json()["role"] == "teacher"

    deactivated = client.post(f"/api/v1/users/{user_id}/deactivate")
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False
