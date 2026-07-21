"""Unit tests for ParentPortalService magic-link roundtrip."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlparse

import pytest
from app.application.parent_portal.magic_link_service import (
    CaptureMagicLinkMailer,
    ParentPortalService,
)
from app.domain.identity.exceptions import InvalidCredentialsError
from app.domain.parent_portal import MagicLinkToken
from app.infrastructure.persistence.models import UserRole
from app.infrastructure.security.jwt_token_service import JwtTokenService


class _MemoryMagicLinkRepo:
    def __init__(self) -> None:
        self._rows: dict[uuid.UUID, MagicLinkToken] = {}
        self._by_hash: dict[str, uuid.UUID] = {}

    async def add(self, token: MagicLinkToken) -> MagicLinkToken:
        self._rows[token.id] = token
        self._by_hash[token.token_hash] = token.id
        return token

    async def get_by_raw_token(self, raw_token: str) -> MagicLinkToken | None:
        from app.domain.parent_portal import hash_magic_token

        token_id = self._by_hash.get(hash_magic_token(raw_token))
        if token_id is None:
            return None
        return self._rows.get(token_id)

    async def save(self, token: MagicLinkToken) -> MagicLinkToken:
        self._rows[token.id] = token
        return token


def _parent_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        email="parent@example.com",
        full_name="Pat Parent",
        role=UserRole.PARENT,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_request_and_consume_magic_link_issues_parent_jwt() -> None:
    parent = _parent_user()
    session = AsyncMock()
    session.get = AsyncMock(return_value=parent)
    mailer = CaptureMagicLinkMailer()
    service = ParentPortalService(
        session=session,
        token_service=JwtTokenService(
            secret="test-secret",
            access_expire_minutes=15,
            refresh_expire_days=7,
        ),
        mailer=mailer,
        expose_magic_url=True,
    )
    service._magic_links = _MemoryMagicLinkRepo()  # type: ignore[method-assign]

    async def _load(*, tenant_slug: str, email: str) -> SimpleNamespace | None:
        assert tenant_slug == "acme"
        assert email == parent.email
        return parent

    service._load_active_parent = _load  # type: ignore[method-assign]

    requested = await service.request_magic_link(
        tenant_slug="acme",
        email=parent.email,
    )
    assert requested.magic_url is not None
    assert mailer.last_magic_url == requested.magic_url
    raw_token = parse_qs(urlparse(requested.magic_url).query)["token"][0]

    tokens = await service.consume_magic_link(raw_token=raw_token)
    assert tokens.user.role == "parent"
    assert tokens.user.email == parent.email
    assert tokens.access_token

    with pytest.raises(InvalidCredentialsError):
        await service.consume_magic_link(raw_token=raw_token)


@pytest.mark.asyncio
async def test_request_unknown_parent_still_accepted() -> None:
    session = AsyncMock()
    mailer = CaptureMagicLinkMailer()
    service = ParentPortalService(
        session=session,
        token_service=JwtTokenService(
            secret="test-secret",
            access_expire_minutes=15,
            refresh_expire_days=7,
        ),
        mailer=mailer,
        expose_magic_url=True,
    )

    async def _load(*, tenant_slug: str, email: str) -> None:
        return None

    service._load_active_parent = _load  # type: ignore[method-assign]
    result = await service.request_magic_link(
        tenant_slug="acme",
        email="missing@example.com",
    )
    assert result.accepted is True
    assert result.magic_url is None
    assert mailer.last_magic_url is None
