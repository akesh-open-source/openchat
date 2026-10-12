from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.messaging.application.commands.list_messages import ListMessagesQuery
from app.messaging.application.commands.send_message import SendMessageCommand
from app.messaging.application.dto.message_list_cursor import MessageListCursor
from app.messaging.application.services.list_messages_service import ListMessagesService
from app.messaging.application.services.send_message_service import SendMessageService
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import ConversationNotFoundError, InvalidCursorError
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
)


def _repos() -> tuple[
    InMemoryMembershipRepository,
    InMemoryConversationRepository,
    InMemoryMessageRepository,
]:
    memberships = InMemoryMembershipRepository()
    conversations = InMemoryConversationRepository(memberships)
    messages = InMemoryMessageRepository(conversations)
    return memberships, conversations, messages


async def _seed_with_messages(count: int) -> tuple[
    ListMessagesService,
    Conversation,
    object,
]:
    memberships, conversations, messages = _repos()
    user_a = uuid4()
    user_b = uuid4()
    conversation = Conversation.create_direct(user_a_id=user_a, user_b_id=user_b)
    await conversations.save(conversation)
    await memberships.save_many(
        [
            Membership.create(
                conversation_id=conversation.id,
                user_id=user_a,
                role=MembershipRole.MEMBER,
            ),
            Membership.create(
                conversation_id=conversation.id,
                user_id=user_b,
            ),
        ]
    )
    send = SendMessageService(
        membership_repository=memberships,
        message_repository=messages,
    )
    for i in range(1, count + 1):
        await send.execute(
            SendMessageCommand(
                user_id=user_a,
                conversation_id=conversation.id,
                client_message_id=f"c{i}",
                body=f"msg-{i}",
            )
        )
    list_service = ListMessagesService(
        membership_repository=memberships,
        message_repository=messages,
    )
    return list_service, conversation, user_a


def test_message_list_cursor_roundtrip() -> None:
    cursor = MessageListCursor(sequence=42)
    restored = MessageListCursor.decode(cursor.encode())
    assert restored.sequence == 42


def test_message_list_cursor_rejects_garbage() -> None:
    with pytest.raises(InvalidCursorError):
        MessageListCursor.decode("not-a-cursor")


def test_list_messages_pages_are_contiguous_by_sequence() -> None:
    async def _run() -> None:
        service, conversation, user_a = await _seed_with_messages(5)
        first = await service.execute(
            ListMessagesQuery(
                user_id=user_a,
                conversation_id=conversation.id,
                limit=2,
            )
        )
        assert [m.sequence for m in first.items] == [1, 2]
        assert first.next_cursor is not None

        second = await service.execute(
            ListMessagesQuery(
                user_id=user_a,
                conversation_id=conversation.id,
                limit=2,
                cursor=first.next_cursor,
            )
        )
        assert [m.sequence for m in second.items] == [3, 4]
        assert second.next_cursor is not None

        third = await service.execute(
            ListMessagesQuery(
                user_id=user_a,
                conversation_id=conversation.id,
                limit=2,
                cursor=second.next_cursor,
            )
        )
        assert [m.sequence for m in third.items] == [5]
        assert third.next_cursor is None

    asyncio.run(_run())


def test_list_messages_rejects_non_member() -> None:
    async def _run() -> None:
        service, conversation, _user_a = await _seed_with_messages(1)
        with pytest.raises(ConversationNotFoundError):
            await service.execute(
                ListMessagesQuery(
                    user_id=uuid4(),
                    conversation_id=conversation.id,
                    limit=10,
                )
            )

    asyncio.run(_run())
