"""Unit tests for parent portal API routes with dependency overrides."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from urllib.parse import parse_qs, urlparse

import pytest
from app.api.v1.parent import get_parent_portal_service
from app.application.identity.auth_service import AuthenticatedUser, AuthTokens
from app.application.parent_portal.magic_link_service import (
    LinkedStudentSummary,
    MagicLinkRequestResult,
    ParentPortalService,
)
from app.domain.parent_portal import ParentStudentLink
from app.main import create_app
from fastapi.testclient import TestClient


class _FakeParentPortalService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self.parent_user_id = uuid.uuid4()
        self._token = "opaque-magic-token-value-123456"
        self._linked: list[LinkedStudentSummary] = []

    async def request_magic_link(self, **kwargs: object) -> MagicLinkRequestResult:
        return MagicLinkRequestResult(
            accepted=True,
            magic_url=(
                "http://localhost:3000/parent/magic-link"
                f"?token={self._token}&tenant={kwargs['tenant_slug']}"
            ),
        )

    async def consume_magic_link(self, *, raw_token: str) -> AuthTokens:
        assert raw_token == self._token
        user = AuthenticatedUser(
            id=self.parent_user_id,
            tenant_id=self.tenant_id,
            email="parent@example.com",
            full_name="Pat Parent",
            role="parent",
        )
        return AuthTokens(
            access_token="access.jwt",
            refresh_token="refresh.jwt",
            user=user,
        )

    async def link_student(self, **kwargs: object) -> ParentStudentLink:
        return ParentStudentLink(
            tenant_id=kwargs["tenant_id"],  # type: ignore[arg-type]
            parent_user_id=kwargs["parent_user_id"],  # type: ignore[arg-type]
            student_id=kwargs["student_id"],  # type: ignore[arg-type]
        )

    async def list_linked_students(
        self,
        **kwargs: object,
    ) -> list[LinkedStudentSummary]:
        assert kwargs["parent_user_id"] == self.parent_user_id
        return self._linked


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeParentPortalService()
    app = create_app()

    def _override() -> ParentPortalService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_parent_portal_service] = _override
    with TestClient(app) as test_client:
        test_client.fake_service = fake  # type: ignore[attr-defined]
        yield test_client
    app.dependency_overrides.clear()


def test_magic_link_request_and_consume(client: TestClient) -> None:
    requested = client.post(
        "/api/v1/parent/magic-link/request",
        json={"tenant_slug": "acme", "email": "parent@example.com"},
    )
    assert requested.status_code == 202
    magic_url = requested.json()["magic_url"]
    assert magic_url is not None
    raw_token = parse_qs(urlparse(magic_url).query)["token"][0]

    consumed = client.post(
        "/api/v1/parent/magic-link/consume",
        json={"token": raw_token},
    )
    assert consumed.status_code == 200
    body = consumed.json()
    assert body["access_token"] == "access.jwt"
    assert body["user"]["role"] == "parent"
