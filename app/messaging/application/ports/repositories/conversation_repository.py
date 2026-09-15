from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.messaging.application.dto.conversation_list_cursor import ConversationListCursor
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

    async def list_for_user(
        self,
        user_id: UUID,
        *,
        limit: int,
        cursor: ConversationListCursor | None = None,
    ) -> list[Conversation]:
        """Return conversations the user is a member of (newest activity first).

        Returns at most ``limit`` rows. Callers may fetch ``limit + 1`` via a
        higher limit to detect a next page.
        """
        ...

    async def save(self, conversation: Conversation) -> None:
        """Insert a new conversation (does not upsert)."""
        ...
