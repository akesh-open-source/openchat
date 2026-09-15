from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.messaging.domain.entities.conversation import Conversation


class ConversationRepository(Protocol):
    """Port for conversation persistence."""

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Return the conversation, or None if missing."""
        ...

    async def get_direct_between(
        self,
        user_a_id: UUID,
        user_b_id: UUID,
    ) -> Conversation | None:
        """Return the direct conversation for the sorted user pair, or None."""
        ...

    async def save(self, conversation: Conversation) -> None:
        """Insert a new conversation (does not upsert)."""
        ...
