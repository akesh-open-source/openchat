from __future__ import annotations

from dataclasses import dataclass

from app.messaging.application.commands.list_conversations import ListConversationsQuery
from app.messaging.application.dto.conversation_list_cursor import ConversationListCursor
from app.messaging.application.dto.conversation_summary import ConversationSummary
from app.messaging.application.ports.repositories.conversation_repository import (
    ConversationRepository,
)
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.application.ports.users_client import UsersClient
from app.messaging.application.services.conversation_summary_enricher import (
    build_conversation_summaries,
)
from app.messaging.domain.exceptions import DomainError


@dataclass(frozen=True, slots=True)
class ListConversationsResult:
    items: list[ConversationSummary]
    next_cursor: str | None


@dataclass(slots=True)
class ListConversationsService:
    conversation_repository: ConversationRepository
    message_repository: MessageRepository
    users_client: UsersClient

    async def execute(self, query: ListConversationsQuery) -> ListConversationsResult:
        if query.limit < 1 or query.limit > 100:
            raise DomainError("limit must be between 1 and 100")

        cursor: ConversationListCursor | None = None
        if query.cursor:
            cursor = ConversationListCursor.decode(query.cursor)

        # Fetch one extra row to decide whether a next page exists.
        rows = await self.conversation_repository.list_for_user(
            query.user_id,
            limit=query.limit + 1,
            cursor=cursor,
        )
        page = rows[: query.limit]
        items = await build_conversation_summaries(
            conversations=page,
            viewer_id=query.user_id,
            access_token=query.access_token,
            message_repository=self.message_repository,
            users_client=self.users_client,
        )

        next_cursor: str | None = None
        if len(rows) > query.limit:
            last = page[-1]
            next_cursor = ConversationListCursor(
                updated_at=last.updated_at,
                id=last.id,
            ).encode()

        return ListConversationsResult(items=items, next_cursor=next_cursor)
