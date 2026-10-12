from __future__ import annotations

from dataclasses import dataclass

from app.messaging.application.commands.send_message import SendMessageCommand
from app.messaging.application.ports.repositories.membership_repository import (
    MembershipRepository,
)
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import (
    ConversationNotFoundError,
    MessageAlreadyExistsError,
)


@dataclass(frozen=True, slots=True)
class SendMessageResult:
    message: Message
    created: bool


@dataclass(slots=True)
class SendMessageService:
    membership_repository: MembershipRepository
    message_repository: MessageRepository

    async def execute(self, command: SendMessageCommand) -> SendMessageResult:
        membership = await self.membership_repository.get(
            command.conversation_id,
            command.user_id,
        )
        if membership is None:
            # Same 404 for missing conversation and non-member (no existence leak).
            raise ConversationNotFoundError("Conversation not found")

        client_message_id = command.client_message_id.strip()
        existing = await self.message_repository.get_by_client_message_id(
            command.conversation_id,
            client_message_id,
        )
        if existing is not None:
            return SendMessageResult(message=existing, created=False)

        try:
            message = await self.message_repository.create_with_next_sequence(
                conversation_id=command.conversation_id,
                sender_id=command.user_id,
                client_message_id=client_message_id,
                body=command.body,
            )
        except MessageAlreadyExistsError:
            # Concurrent retry with the same client_message_id.
            raced = await self.message_repository.get_by_client_message_id(
                command.conversation_id,
                client_message_id,
            )
            if raced is None:
                raise
            return SendMessageResult(message=raced, created=False)

        return SendMessageResult(message=message, created=True)
