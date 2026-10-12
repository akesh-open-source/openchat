from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.messaging.domain.entities.membership import Membership


class MembershipRepository(Protocol):
    """Port for conversation membership persistence."""

    async def get(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Membership | None:
        """Return membership for the user in the conversation, or None."""
        ...

    async def list_by_conversation(self, conversation_id: UUID) -> list[Membership]:
        """Return all memberships for a conversation."""
        ...

    async def list_by_user(self, user_id: UUID) -> list[Membership]:
        """Return all memberships for a user."""
        ...

    async def save(self, membership: Membership) -> None:
        """Insert a new membership (does not upsert)."""
        ...

    async def save_many(self, memberships: list[Membership]) -> None:
        """Insert multiple memberships in one flush."""
        ...
