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

    async def get_by_client_message_id(
        self,
        conversation_id: UUID,
        client_message_id: str,
    ) -> Message | None:
        """Return the message for this client idempotency key, or None."""
        ...

    async def create_with_next_sequence(
        self,
        *,
        conversation_id: UUID,
        sender_id: UUID,
        client_message_id: str,
        body: str,
    ) -> Message:
        """Lock conversation, assign ``sequence``, insert message in one unit.

        Raises ``MessageAlreadyExistsError`` on unique conflicts.
        Raises ``ConversationNotFoundError`` if the conversation row is missing.
        """
        ...

    async def save(self, message: Message) -> None:
        """Insert a new message (does not upsert)."""
        ...
