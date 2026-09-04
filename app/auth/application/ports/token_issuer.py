from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenIssuer(Protocol):
    """Port for issuing and validating auth tokens."""

    def issue_tokens(self, user_id: UUID, email: str) -> TokenPair:
        ...

    def verify_access_token(self, token: str) -> UUID:
        """Return the subject user id, or raise on invalid/expired token."""
        ...
