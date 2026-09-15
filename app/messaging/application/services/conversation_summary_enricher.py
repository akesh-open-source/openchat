from __future__ import annotations

import logging
from uuid import UUID

from app.messaging.application.dto.conversation_summary import ConversationSummary
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.application.ports.users_client import UsersClient
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import UsersUnavailableError

logger = logging.getLogger(__name__)

_PREVIEW_MAX_LEN = 200


def _preview_body(body: str) -> str:
    text = body.strip()
    if len(text) <= _PREVIEW_MAX_LEN:
        return text
    return text[: _PREVIEW_MAX_LEN - 1] + "…"


async def build_conversation_summaries(
    *,
    conversations: list[Conversation],
    viewer_id: UUID,
    access_token: str,
    message_repository: MessageRepository,
    users_client: UsersClient,
) -> list[ConversationSummary]:
    """Enrich conversations with peer display names and last-message previews."""
    if not conversations:
        return []

    latest_by_conversation = await message_repository.get_latest_by_conversation_ids(
        [conversation.id for conversation in conversations],
    )

    bases = [
        ConversationSummary.from_conversation(conversation, viewer_id=viewer_id)
        for conversation in conversations
    ]
    peer_ids = [
        summary.peer_user_id
        for summary in bases
        if summary.peer_user_id is not None
    ]

    display_names: dict[UUID, str] = {}
    if peer_ids:
        try:
            display_names = await users_client.get_display_names(
                user_ids=peer_ids,
                access_token=access_token,
            )
        except UsersUnavailableError:
            # List/detail should still succeed; names stay null until users recovers.
            logger.warning("Skipping peer display names; users service unavailable")

    enriched: list[ConversationSummary] = []
    for summary in bases:
        last_message: Message | None = latest_by_conversation.get(summary.id)
        last_preview = (
            _preview_body(last_message.body) if last_message is not None else None
        )
        last_at = last_message.created_at if last_message is not None else None
        last_activity = last_at or summary.updated_at
        peer_name = (
            display_names.get(summary.peer_user_id)
            if summary.peer_user_id is not None
            else None
        )
        enriched.append(
            ConversationSummary(
                id=summary.id,
                type=summary.type,
                peer_user_id=summary.peer_user_id,
                peer_display_name=peer_name,
                last_message_preview=last_preview,
                last_message_at=last_at,
                last_activity_at=last_activity,
                created_at=summary.created_at,
                updated_at=summary.updated_at,
            )
        )
    return enriched
