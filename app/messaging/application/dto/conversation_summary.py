from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.value_objects.conversation_type import ConversationType


@dataclass(frozen=True, slots=True)
class ConversationSummary:
    """List/detail projection for a conversation the caller may see."""

    id: UUID
    type: ConversationType
    peer_user_id: UUID | None
    peer_display_name: str | None
    last_message_preview: str | None
    last_message_at: datetime | None
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_conversation(
        cls,
        conversation: Conversation,
        *,
        viewer_id: UUID,
    ) -> ConversationSummary:
        peer_user_id: UUID | None = None
        if conversation.is_direct:
            if conversation.direct_user_a_id == viewer_id:
                peer_user_id = conversation.direct_user_b_id
            else:
                peer_user_id = conversation.direct_user_a_id

        return cls(
            id=conversation.id,
            type=conversation.type,
            peer_user_id=peer_user_id,
            peer_display_name=None,
            last_message_preview=None,
            last_message_at=None,
            last_activity_at=conversation.updated_at,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
