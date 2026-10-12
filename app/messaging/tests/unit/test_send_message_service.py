from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.messaging.application.commands.send_message import SendMessageCommand
from app.messaging.application.services.send_message_service import SendMessageService
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import ConversationNotFoundError
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
)


def _service() -> tuple[
    SendMessageService,
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
]:
    memberships = InMemoryMembershipRepository()
    conversations = InMemoryConversationRepository(memberships)
    messages = InMemoryMessageRepository(conversations)
    service = SendMessageService(
        membership_repository=memberships,
        message_repository=messages,
    )
    return service, conversations, memberships, messages


async def _seed_direct() -> tuple[
    SendMessageService,
    Conversation,
    object,
    object,
]:
    service, conversations, memberships, _messages = _service()
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
    return service, conversation, user_a, user_b


def test_send_assigns_contiguous_sequences() -> None:
    async def _run() -> None:
        service, conversation, user_a, _user_b = await _seed_direct()
        first = await service.execute(
            SendMessageCommand(
                user_id=user_a,
                conversation_id=conversation.id,
                client_message_id="c1",
                body="one",
            )
        )
        second = await service.execute(
            SendMessageCommand(
                user_id=user_a,
                conversation_id=conversation.id,
                client_message_id="c2",
                body="two",
            )
        )
        assert first.created is True
        assert first.message.sequence == 1
        assert second.message.sequence == 2

    asyncio.run(_run())


def test_send_idempotent_on_client_message_id() -> None:
    async def _run() -> None:
        service, conversation, user_a, _user_b = await _seed_direct()
        first = await service.execute(
            SendMessageCommand(
                user_id=user_a,
                conversation_id=conversation.id,
                client_message_id="same",
                body="hello",
            )
        )
        again = await service.execute(
            SendMessageCommand(
                user_id=user_a,
                conversation_id=conversation.id,
                client_message_id="same",
                body="hello",
            )
        )
        assert again.created is False
        assert again.message.id == first.message.id
        assert again.message.sequence == first.message.sequence

    asyncio.run(_run())


def test_send_rejects_non_member() -> None:
    async def _run() -> None:
        service, conversation, _user_a, _user_b = await _seed_direct()
        with pytest.raises(ConversationNotFoundError):
            await service.execute(
                SendMessageCommand(
                    user_id=uuid4(),
                    conversation_id=conversation.id,
                    client_message_id="x",
                    body="nope",
                )
            )

    asyncio.run(_run())
