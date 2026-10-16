from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.messaging.domain.entities.message import Message

MESSAGE_CREATED = "message.created"


@dataclass(slots=True)
class OutboxEvent:
    """Transactional outbox row (publish to Kafka happens in a later slice)."""

    id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    conversation_id: UUID
    payload: dict[str, Any]
    created_at: datetime
    published_at: datetime | None = None

    @classmethod
    def for_message_created(cls, message: Message) -> OutboxEvent:
        return cls(
            id=uuid4(),
            event_type=MESSAGE_CREATED,
            aggregate_type="message",
            aggregate_id=message.id,
            conversation_id=message.conversation_id,
            payload={
                "message_id": str(message.id),
                "conversation_id": str(message.conversation_id),
                "sender_id": str(message.sender_id),
                "client_message_id": message.client_message_id,
                "sequence": message.sequence,
                "body": message.body,
                "status": message.status.value,
                "created_at": message.created_at.isoformat(),
            },
            created_at=datetime.now(timezone.utc),
            published_at=None,
        )
