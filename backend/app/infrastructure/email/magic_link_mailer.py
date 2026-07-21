"""Magic-link email delivery adapters."""

from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class MagicLinkMailer(Protocol):
    """Port for delivering magic-link login emails."""

    async def send_magic_link(self, *, to_email: str, magic_url: str) -> None:
        """Deliver ``magic_url`` to ``to_email``."""
        ...


class LoggingMagicLinkMailer:
    """Development mailer that logs the magic URL instead of sending email."""

    async def send_magic_link(self, *, to_email: str, magic_url: str) -> None:
        """Log the outbound magic link for local/dev verification."""
        logger.info("Magic link for %s: %s", to_email, magic_url)
