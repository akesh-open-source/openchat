from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.messaging.application.commands.get_conversation import GetConversationQuery
from app.messaging.application.commands.list_conversations import ListConversationsQuery
from app.messaging.application.dto.conversation_list_cursor import ConversationListCursor
from app.messaging.application.services.get_conversation_service import (
    GetConversationService,
)
from app.messaging.application.services.list_conversations_service import (
    ListConversationsService,
)
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import ConversationNotFoundError, InvalidCursorError
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
)


def test_conversation_list_cursor_roundtrip() -> None:
    cursor = ConversationListCursor(
        updated_at=datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc),
        id=uuid4(),
    )
    restored = ConversationListCursor.decode(cursor.encode())
    assert restored.id == cursor.id
    assert restored.updated_at == cursor.updated_at


def test_conversation_list_cursor_rejects_garbage() -> None:
    with pytest.raises(InvalidCursorError):
        ConversationListCursor.decode("not-a-cursor")


def test_list_conversations_paginates_and_filters_membership() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
        service = ListConversationsService(conversation_repository=conversations)

        user_id = uuid4()
        outsider = uuid4()
        base = datetime.now(timezone.utc)

        created_ids: list = []
        for offset in range(3):
            peer = uuid4()
            conversation = Conversation.create_direct(
                user_a_id=user_id,
                user_b_id=peer,
            )
            conversation.updated_at = base + timedelta(minutes=offset)
            conversation.created_at = conversation.updated_at
            await conversations.save(conversation)
            await memberships.save_many(
                [
                    Membership.create(
                        conversation_id=conversation.id,
                        user_id=user_id,
                    ),
                    Membership.create(
                        conversation_id=conversation.id,
                        user_id=peer,
                    ),
                ]
            )
            created_ids.append(conversation.id)

        # Conversation the user is not in.
        other = Conversation.create_direct(user_a_id=outsider, user_b_id=uuid4())
        await conversations.save(other)
        await memberships.save_many(
            [
                Membership.create(conversation_id=other.id, user_id=outsider),
                Membership.create(
                    conversation_id=other.id,
                    user_id=other.direct_user_b_id,  # type: ignore[arg-type]
                ),
            ]
        )

        first_page = await service.execute(
            ListConversationsQuery(user_id=user_id, limit=2),
        )
        assert len(first_page.items) == 2
        assert first_page.next_cursor is not None
        assert {item.id for item in first_page.items}.isdisjoint({other.id})

        second_page = await service.execute(
            ListConversationsQuery(
                user_id=user_id,
                limit=2,
                cursor=first_page.next_cursor,
            ),
        )
        assert len(second_page.items) == 1
        assert second_page.next_cursor is None
        assert {item.id for item in first_page.items} | {
            item.id for item in second_page.items
        } == set(created_ids)

    asyncio.run(_run())


def test_get_conversation_requires_membership() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
        service = GetConversationService(
            conversation_repository=conversations,
            membership_repository=memberships,
        )

        owner = uuid4()
        peer = uuid4()
        stranger = uuid4()
        conversation = Conversation.create_direct(user_a_id=owner, user_b_id=peer)
        await conversations.save(conversation)
        await memberships.save_many(
            [
                Membership.create(conversation_id=conversation.id, user_id=owner),
                Membership.create(conversation_id=conversation.id, user_id=peer),
            ]
        )

        summary = await service.execute(
            GetConversationQuery(user_id=owner, conversation_id=conversation.id),
        )
        assert summary.id == conversation.id
        assert summary.peer_user_id == peer
        assert summary.peer_display_name is None

        with pytest.raises(ConversationNotFoundError):
            await service.execute(
                GetConversationQuery(
                    user_id=stranger,
                    conversation_id=conversation.id,
                ),
            )

    asyncio.run(_run())
