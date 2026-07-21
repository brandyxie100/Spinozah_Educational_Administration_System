"""Password hashing port for the identity context."""

from __future__ import annotations

from typing import Protocol


class PasswordHasher(Protocol):
    """Hash and verify passwords without leaking infrastructure details."""

    def hash(self, plain_password: str) -> str:
        """Return a one-way digest for storage."""

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Return True when plain_password matches the stored digest."""
