from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.messaging.domain.entities.message import Message


class MessageRepository(Protocol):
    """Port for message persistence."""

    async def get_latest_by_conversation_ids(
        self,
        conversation_ids: list[UUID],
    ) -> dict[UUID, Message]:
        """Return the highest-sequence message per conversation id (if any)."""
        ...

    async def save(self, message: Message) -> None:
        """Insert a new message (does not upsert)."""
        ...
