from __future__ import annotations

from app.messaging.domain.entities.message import Message
from app.messaging.domain.value_objects.message_status import MessageStatus
from app.messaging.infrastructure.persistence.postgres.models.message import MessageModel


def to_domain(model: MessageModel) -> Message:
    return Message(
        id=model.id,
        conversation_id=model.conversation_id,
        sender_id=model.sender_id,
        client_message_id=model.client_message_id,
        sequence=model.sequence,
        body=model.body,
        status=MessageStatus(model.status),
        created_at=model.created_at,
    )


def to_model(message: Message) -> MessageModel:
    return MessageModel(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        client_message_id=message.client_message_id,
        sequence=message.sequence,
        body=message.body,
        status=message.status.value,
        created_at=message.created_at,
    )
