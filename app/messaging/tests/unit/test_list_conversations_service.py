from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
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
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import (
    ConversationNotFoundError,
    InvalidCursorError,
    UsersUnavailableError,
)
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
)


def _list_service(
    conversations: InMemoryConversationRepository,
    messages: InMemoryMessageRepository,
    users_client: MagicMock,
) -> ListConversationsService:
    return ListConversationsService(
        conversation_repository=conversations,
        message_repository=messages,
        users_client=users_client,
    )


def _get_service(
    conversations: InMemoryConversationRepository,
    memberships: InMemoryMembershipRepository,
    messages: InMemoryMessageRepository,
    users_client: MagicMock,
) -> GetConversationService:
    return GetConversationService(
        conversation_repository=conversations,
        membership_repository=memberships,
        message_repository=messages,
        users_client=users_client,
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
        messages = InMemoryMessageRepository()
        users_client = MagicMock()
        users_client.get_display_names = AsyncMock(return_value={})
        service = _list_service(conversations, messages, users_client)

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
            ListConversationsQuery(
                user_id=user_id,
                access_token="tok",
                limit=2,
            ),
        )
        assert len(first_page.items) == 2
        assert first_page.next_cursor is not None
        assert {item.id for item in first_page.items}.isdisjoint({other.id})

        second_page = await service.execute(
            ListConversationsQuery(
                user_id=user_id,
                access_token="tok",
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


def test_list_conversations_enriches_peer_name_and_last_message() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
        messages = InMemoryMessageRepository()
        user_id = uuid4()
        peer = uuid4()
        conversation = Conversation.create_direct(user_a_id=user_id, user_b_id=peer)
        await conversations.save(conversation)
        await memberships.save_many(
            [
                Membership.create(conversation_id=conversation.id, user_id=user_id),
                Membership.create(conversation_id=conversation.id, user_id=peer),
            ]
        )
        message = Message.create(
            conversation_id=conversation.id,
            sender_id=peer,
            client_message_id="m1",
            sequence=1,
            body="hello there",
        )
        await messages.save(message)

        users_client = MagicMock()
        users_client.get_display_names = AsyncMock(return_value={peer: "Ada"})
        service = _list_service(conversations, messages, users_client)

        result = await service.execute(
            ListConversationsQuery(user_id=user_id, access_token="tok"),
        )
        assert len(result.items) == 1
        item = result.items[0]
        assert item.peer_user_id == peer
        assert item.peer_display_name == "Ada"
        assert item.last_message_preview == "hello there"
        assert item.last_message_at == message.created_at
        assert item.last_activity_at == message.created_at
        users_client.get_display_names.assert_awaited_once()

    asyncio.run(_run())


def test_list_conversations_soft_fails_when_users_unavailable() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
        messages = InMemoryMessageRepository()
        user_id = uuid4()
        peer = uuid4()
        conversation = Conversation.create_direct(user_a_id=user_id, user_b_id=peer)
        await conversations.save(conversation)
        await memberships.save_many(
            [
                Membership.create(conversation_id=conversation.id, user_id=user_id),
                Membership.create(conversation_id=conversation.id, user_id=peer),
            ]
        )

        users_client = MagicMock()
        users_client.get_display_names = AsyncMock(
            side_effect=UsersUnavailableError("down"),
        )
        service = _list_service(conversations, messages, users_client)

        result = await service.execute(
            ListConversationsQuery(user_id=user_id, access_token="tok"),
        )
        assert result.items[0].peer_display_name is None
        assert result.items[0].last_message_preview is None

    asyncio.run(_run())


def test_get_conversation_requires_membership() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
        messages = InMemoryMessageRepository()
        users_client = MagicMock()
        users_client.get_display_names = AsyncMock(return_value={})
        service = _get_service(conversations, memberships, messages, users_client)

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
            GetConversationQuery(
                user_id=owner,
                conversation_id=conversation.id,
                access_token="tok",
            ),
        )
        assert summary.id == conversation.id
        assert summary.peer_user_id == peer
        assert summary.peer_display_name is None

        with pytest.raises(ConversationNotFoundError):
            await service.execute(
                GetConversationQuery(
                    user_id=stranger,
                    conversation_id=conversation.id,
                    access_token="tok",
                ),
            )

    asyncio.run(_run())
