"""bcrypt-backed password hasher."""

from __future__ import annotations

import bcrypt


class BcryptPasswordHasher:
    """Hash and verify passwords with bcrypt."""

    def hash(self, plain_password: str) -> str:
        """Return a bcrypt digest for storage."""
        digest = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt(),
        )
        return digest.decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Return True when plain_password matches the stored digest."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except ValueError:
            # Malformed hash — treat as non-match (fail closed).
            return False
