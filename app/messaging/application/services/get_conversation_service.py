from __future__ import annotations

from dataclasses import dataclass

from app.messaging.application.commands.get_conversation import GetConversationQuery
from app.messaging.application.dto.conversation_summary import ConversationSummary
from app.messaging.application.ports.repositories.conversation_repository import (
    ConversationRepository,
)
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.application.ports.users_client import UsersClient
from app.messaging.application.services.conversation_membership_guard import (
    ConversationMembershipGuard,
)
from app.messaging.application.services.conversation_summary_enricher import (
    build_conversation_summaries,
)
from app.messaging.domain.exceptions import ConversationNotFoundError


@dataclass(slots=True)
class GetConversationService:
    conversation_repository: ConversationRepository
    membership_guard: ConversationMembershipGuard
    message_repository: MessageRepository
    users_client: UsersClient

    async def execute(self, query: GetConversationQuery) -> ConversationSummary:
        await self.membership_guard.require_member(
            conversation_id=query.conversation_id,
            user_id=query.user_id,
        )

        conversation = await self.conversation_repository.get_by_id(
            query.conversation_id,
        )
        if conversation is None:
            # Membership without conversation row should not leak differently.
            raise ConversationNotFoundError("Conversation not found")

        summaries = await build_conversation_summaries(
            conversations=[conversation],
            viewer_id=query.user_id,
            access_token=query.access_token,
            message_repository=self.message_repository,
            users_client=self.users_client,
        )
        return summaries[0]
