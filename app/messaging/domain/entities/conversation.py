from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.messaging.domain.value_objects.conversation_type import ConversationType
from app.messaging.domain.value_objects.user_pair import sorted_user_pair


@dataclass(slots=True)
class Conversation:
    """Chat conversation aggregate (direct now; group later)."""

    id: UUID
    type: ConversationType
    created_at: datetime
    updated_at: datetime
    # Sorted auth user ids for direct chats; both None for group.
    direct_user_a_id: UUID | None = None
    direct_user_b_id: UUID | None = None
    # Monotonic sequence allocator for messages (bumped on send).
    next_sequence: int = 0

    @classmethod
    def create_direct(
        cls,
        *,
        user_a_id: UUID,
        user_b_id: UUID,
        conversation_id: UUID | None = None,
    ) -> Conversation:
        user_a, user_b = sorted_user_pair(user_a_id, user_b_id)
        now = datetime.now(timezone.utc)
        return cls(
            id=conversation_id or uuid4(),
            type=ConversationType.DIRECT,
            direct_user_a_id=user_a,
            direct_user_b_id=user_b,
            created_at=now,
            updated_at=now,
            next_sequence=0,
        )

    @property
    def is_direct(self) -> bool:
        return self.type is ConversationType.DIRECT
