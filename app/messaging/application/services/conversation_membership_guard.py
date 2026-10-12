from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.messaging.application.ports.repositories.membership_repository import (
    MembershipRepository,
)
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import ConversationNotFoundError


@dataclass(slots=True)
class ConversationMembershipGuard:
    """Central membership authz for conversation-scoped message routes.

    Missing membership and missing conversation are indistinguishable to the
    caller: both raise ``ConversationNotFoundError`` → HTTP 404 (never 403).
    Authorization is based only on server-side membership rows — never on
    client-supplied flags.
    """

    membership_repository: MembershipRepository

    async def require_member(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Membership:
        membership = await self.membership_repository.get(conversation_id, user_id)
        if membership is None:
            raise ConversationNotFoundError("Conversation not found")
        return membership
