from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.auth.application.commands.revoke_session import RevokeSessionCommand
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.session_repository import SessionRepository
from app.auth.domain.exceptions import SessionNotFoundError


@dataclass(slots=True)
class RevokeSessionService:
    session_repository: SessionRepository
    refresh_token_repository: RefreshTokenRepository

    async def revoke_session(self, command: RevokeSessionCommand) -> None:
        session = await self.session_repository.get_by_id(command.session_id)
        if session is None or session.user_id != command.user_id:
            raise SessionNotFoundError("Session not found")

        now = datetime.now(timezone.utc)
        await self.session_repository.revoke_by_id(
            command.session_id,
            command.user_id,
            at=now,
        )
        await self.refresh_token_repository.revoke_all_for_session(
            command.session_id,
            at=now,
        )
