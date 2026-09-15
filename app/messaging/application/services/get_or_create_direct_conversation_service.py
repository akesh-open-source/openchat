from __future__ import annotations

from dataclasses import dataclass

from app.messaging.application.commands.get_or_create_direct_conversation import (
    GetOrCreateDirectConversationCommand,
)
from app.messaging.application.ports.repositories.conversation_repository import (
    ConversationRepository,
)
from app.messaging.application.ports.repositories.membership_repository import (
    MembershipRepository,
)
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import ConversationAlreadyExistsError
from app.messaging.domain.value_objects.membership_role import MembershipRole


@dataclass(frozen=True, slots=True)
class GetOrCreateDirectConversationResult:
    conversation: Conversation
    created: bool


@dataclass(slots=True)
class GetOrCreateDirectConversationService:
    """Create a direct conversation or return the existing one for the pair.

    Peer existence is not validated against the users service for MVP — the
    gateway/client is trusted to pass a real peer_user_id (see API docs).
    """

    conversation_repository: ConversationRepository
    membership_repository: MembershipRepository

    async def execute(
        self,
        command: GetOrCreateDirectConversationCommand,
    ) -> GetOrCreateDirectConversationResult:
        existing = await self.conversation_repository.get_direct_between(
            command.user_id,
            command.peer_user_id,
        )
        if existing is not None:
            return GetOrCreateDirectConversationResult(
                conversation=existing,
                created=False,
            )

        conversation = Conversation.create_direct(
            user_a_id=command.user_id,
            user_b_id=command.peer_user_id,
        )

        try:
            await self.conversation_repository.save(conversation)
        except ConversationAlreadyExistsError:
            raced = await self.conversation_repository.get_direct_between(
                command.user_id,
                command.peer_user_id,
            )
            if raced is None:
                raise
            return GetOrCreateDirectConversationResult(
                conversation=raced,
                created=False,
            )

        await self.membership_repository.save_many(
            [
                Membership.create(
                    conversation_id=conversation.id,
                    user_id=command.user_id,
                    role=MembershipRole.MEMBER,
                ),
                Membership.create(
                    conversation_id=conversation.id,
                    user_id=command.peer_user_id,
                    role=MembershipRole.MEMBER,
                ),
            ]
        )
        return GetOrCreateDirectConversationResult(
            conversation=conversation,
            created=True,
        )
