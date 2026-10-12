from __future__ import annotations

from dataclasses import dataclass

from app.messaging.application.commands.list_messages import ListMessagesQuery
from app.messaging.application.dto.message_list_cursor import MessageListCursor
from app.messaging.application.ports.repositories.membership_repository import (
    MembershipRepository,
)
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import ConversationNotFoundError, DomainError


@dataclass(frozen=True, slots=True)
class ListMessagesResult:
    items: list[Message]
    next_cursor: str | None


@dataclass(slots=True)
class ListMessagesService:
    membership_repository: MembershipRepository
    message_repository: MessageRepository

    async def execute(self, query: ListMessagesQuery) -> ListMessagesResult:
        if query.limit < 1 or query.limit > 100:
            raise DomainError("limit must be between 1 and 100")

        membership = await self.membership_repository.get(
            query.conversation_id,
            query.user_id,
        )
        if membership is None:
            # Same 404 for missing conversation and non-member (no existence leak).
            raise ConversationNotFoundError("Conversation not found")

        cursor: MessageListCursor | None = None
        if query.cursor:
            cursor = MessageListCursor.decode(query.cursor)

        # Fetch one extra row to decide whether a next page exists.
        rows = await self.message_repository.list_by_conversation(
            query.conversation_id,
            limit=query.limit + 1,
            cursor=cursor,
        )
        page = rows[: query.limit]

        next_cursor: str | None = None
        if len(rows) > query.limit:
            last = page[-1]
            next_cursor = MessageListCursor(sequence=last.sequence).encode()

        return ListMessagesResult(items=page, next_cursor=next_cursor)
