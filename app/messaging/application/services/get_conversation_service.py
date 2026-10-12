from __future__ import annotations

from dataclasses import dataclass

from app.messaging.application.commands.get_conversation import GetConversationQuery
from app.messaging.application.dto.conversation_summary import ConversationSummary
from app.messaging.application.ports.repositories.conversation_repository import (
    ConversationRepository,
)
from app.messaging.application.ports.repositories.membership_repository import (
    MembershipRepository,
)
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.application.ports.users_client import UsersClient
from app.messaging.application.services.conversation_summary_enricher import (
    build_conversation_summaries,
)
from app.messaging.domain.exceptions import ConversationNotFoundError


@dataclass(slots=True)
class GetConversationService:
    conversation_repository: ConversationRepository
    membership_repository: MembershipRepository
    message_repository: MessageRepository
    users_client: UsersClient

    async def execute(self, query: GetConversationQuery) -> ConversationSummary:
        membership = await self.membership_repository.get(
            query.conversation_id,
            query.user_id,
        )
        if membership is None:
            # Same 404 for missing conversation and non-member (no existence leak).
            raise ConversationNotFoundError("Conversation not found")

        conversation = await self.conversation_repository.get_by_id(
            query.conversation_id,
        )
        if conversation is None:
            raise ConversationNotFoundError("Conversation not found")

        summaries = await build_conversation_summaries(
            conversations=[conversation],
            viewer_id=query.user_id,
            access_token=query.access_token,
            message_repository=self.message_repository,
            users_client=self.users_client,
        )
        return summaries[0]
