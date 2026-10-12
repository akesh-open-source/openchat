from __future__ import annotations

from dataclasses import dataclass

from app.messaging.application.commands.send_message import SendMessageCommand
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.application.services.conversation_membership_guard import (
    ConversationMembershipGuard,
)
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import MessageAlreadyExistsError


@dataclass(frozen=True, slots=True)
class SendMessageResult:
    message: Message
    created: bool


@dataclass(slots=True)
class SendMessageService:
    membership_guard: ConversationMembershipGuard
    message_repository: MessageRepository

    async def execute(self, command: SendMessageCommand) -> SendMessageResult:
        await self.membership_guard.require_member(
            conversation_id=command.conversation_id,
            user_id=command.user_id,
        )

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
