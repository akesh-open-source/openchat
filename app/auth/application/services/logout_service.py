from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.auth.application.commands.logout import LogoutCommand
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.session_repository import SessionRepository
from app.auth.application.ports.token_issuer import TokenIssuer
from app.auth.domain.exceptions import InvalidTokenError
from app.auth.infrastructure.security.token_hash import hash_token


@dataclass(slots=True)
class LogoutService:
    token_issuer: TokenIssuer
    refresh_token_repository: RefreshTokenRepository
    session_repository: SessionRepository

    async def logout(self, command: LogoutCommand) -> None:
        """Revoke the session bound to the refresh token (idempotent)."""
        try:
            claims = self.token_issuer.verify_refresh_token(command.refresh_token)
        except InvalidTokenError:
            return

        stored = await self.refresh_token_repository.get_by_id(claims.jti)
        if stored is None:
            return
        if stored.user_id != claims.user_id:
            return
        if stored.token_hash != hash_token(command.refresh_token):
            return

        now = datetime.now(timezone.utc)
        if stored.session_id is not None:
            await self.session_repository.revoke_by_id(
                stored.session_id,
                stored.user_id,
                at=now,
            )
            await self.refresh_token_repository.revoke_all_for_session(
                stored.session_id,
                at=now,
            )
            return

        await self.refresh_token_repository.revoke_family(stored.family_id, at=now)
