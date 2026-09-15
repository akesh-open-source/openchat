from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.messaging.domain.exceptions import DomainError
from app.messaging.domain.value_objects.message_status import MessageStatus


@dataclass(slots=True)
class Message:
    """Persisted chat message with conversation-scoped sequence."""

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    client_message_id: str
    sequence: int
    body: str
    status: MessageStatus
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        conversation_id: UUID,
        sender_id: UUID,
        client_message_id: str,
        sequence: int,
        body: str,
        message_id: UUID | None = None,
    ) -> Message:
        client_id = client_message_id.strip()
        if not client_id:
            raise DomainError("client_message_id must not be empty")
        if len(client_id) > 128:
            raise DomainError("client_message_id must be at most 128 characters")
        if sequence < 1:
            raise DomainError("sequence must be >= 1")
        if not body:
            raise DomainError("body must not be empty")

        return cls(
            id=message_id or uuid4(),
            conversation_id=conversation_id,
            sender_id=sender_id,
            client_message_id=client_id,
            sequence=sequence,
            body=body,
            status=MessageStatus.SENT,
            created_at=datetime.now(timezone.utc),
        )
