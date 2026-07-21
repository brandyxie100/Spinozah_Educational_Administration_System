"""Identity-domain authentication errors."""

from __future__ import annotations


class InvalidCredentialsError(Exception):
    """Raised when login or token validation fails."""
