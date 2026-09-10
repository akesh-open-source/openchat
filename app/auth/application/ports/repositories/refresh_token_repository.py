from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.auth.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(Protocol):
    """Port for refresh-token persistence and revocation."""

    async def get_by_id(self, token_id: UUID) -> RefreshToken | None:
        ...

    async def save(self, token: RefreshToken) -> None:
        """Persist a new refresh token or update an existing one."""
        ...

    async def revoke_family(self, family_id: UUID, *, at: datetime) -> None:
        """Revoke every active token in a rotation family (reuse detection)."""
        ...

    async def revoke_all_for_user(self, user_id: UUID, *, at: datetime) -> None:
        """Revoke every active refresh token for a user (e.g. password change)."""
        ...
