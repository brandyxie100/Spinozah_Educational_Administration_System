"""Email delivery adapters."""

from app.infrastructure.email.magic_link_mailer import (
    LoggingMagicLinkMailer,
    MagicLinkMailer,
)

__all__ = ["LoggingMagicLinkMailer", "MagicLinkMailer"]
