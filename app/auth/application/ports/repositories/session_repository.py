from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.auth.domain.entities.session import Session


class SessionRepository(Protocol):
    async def get_by_id(self, session_id: UUID) -> Session | None:
        ...

    async def list_active_by_user(self, user_id: UUID) -> list[Session]:
        ...

    async def save(self, session: Session) -> None:
        ...

    async def revoke_all_for_user(self, user_id: UUID, *, at: datetime) -> None:
        ...

    async def revoke_by_id(
        self,
        session_id: UUID,
        user_id: UUID,
        *,
        at: datetime,
    ) -> bool:
        """Revoke session if it belongs to user. Returns True if found."""
        ...
