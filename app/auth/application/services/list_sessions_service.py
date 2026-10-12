from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.auth.application.ports.repositories.session_repository import SessionRepository
from app.auth.domain.entities.session import Session


@dataclass(slots=True)
class ListSessionsService:
    session_repository: SessionRepository

    async def list_sessions(self, user_id: UUID) -> list[Session]:
        return await self.session_repository.list_active_by_user(user_id)
