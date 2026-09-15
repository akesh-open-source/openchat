from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

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
        return cls(
            id=message_id or uuid4(),
            conversation_id=conversation_id,
            sender_id=sender_id,
            client_message_id=client_message_id.strip(),
            sequence=sequence,
            body=body,
            status=MessageStatus.SENT,
            created_at=datetime.now(timezone.utc),
        )
