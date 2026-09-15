from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.messaging.domain.value_objects.membership_role import MembershipRole


@dataclass(slots=True)
class Membership:
    """User participation in a conversation."""

    conversation_id: UUID
    user_id: UUID
    role: MembershipRole
    joined_at: datetime

    @classmethod
    def create(
        cls,
        *,
        conversation_id: UUID,
        user_id: UUID,
        role: MembershipRole = MembershipRole.MEMBER,
        joined_at: datetime | None = None,
    ) -> Membership:
        return cls(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            joined_at=joined_at or datetime.now(timezone.utc),
        )
