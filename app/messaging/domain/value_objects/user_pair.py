from __future__ import annotations

from uuid import UUID

from app.messaging.domain.exceptions import SelfConversationError


def sorted_user_pair(user_a: UUID, user_b: UUID) -> tuple[UUID, UUID]:
    """Return (user_a, user_b) ordered so a < b for stable 1:1 uniqueness."""
    if user_a == user_b:
        raise SelfConversationError("Cannot create a conversation with yourself")
    if user_a < user_b:
        return user_a, user_b
    return user_b, user_a
