from __future__ import annotations

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.value_objects.conversation_type import ConversationType
from app.messaging.infrastructure.persistence.postgres.models.conversation import (
    ConversationModel,
)


def to_domain(model: ConversationModel) -> Conversation:
    return Conversation(
        id=model.id,
        type=ConversationType(model.type),
        direct_user_a_id=model.direct_user_a_id,
        direct_user_b_id=model.direct_user_b_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        next_sequence=model.next_sequence,
    )


def to_model(conversation: Conversation) -> ConversationModel:
    return ConversationModel(
        id=conversation.id,
        type=conversation.type.value,
        direct_user_a_id=conversation.direct_user_a_id,
        direct_user_b_id=conversation.direct_user_b_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        next_sequence=conversation.next_sequence,
    )
