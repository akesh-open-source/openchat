from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    refresh_jti: UUID
    refresh_expires_at: datetime
    token_type: str = "bearer"


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    user_id: UUID
    session_id: UUID


@dataclass(frozen=True, slots=True)
class RefreshTokenClaims:
    user_id: UUID
    email: str
    jti: UUID


class TokenIssuer(Protocol):
    """Port for issuing and validating auth tokens."""

    def issue_tokens(
        self,
        user_id: UUID,
        email: str,
        *,
        session_id: UUID,
    ) -> TokenPair:
        ...

    def verify_access_token(self, token: str) -> AccessTokenClaims:
        """Return access claims, or raise on invalid/expired token."""
        ...

    def verify_refresh_token(self, token: str) -> RefreshTokenClaims:
        """Return refresh claims, or raise on invalid/expired refresh token."""
        ...

    def issue_password_reset_token(self, user_id: UUID, email: str) -> str:
        """Return a short-lived password-reset token."""
        ...

    def verify_password_reset_token(self, token: str) -> UUID:
        """Return the subject user id, or raise on invalid/expired reset token."""
        ...
