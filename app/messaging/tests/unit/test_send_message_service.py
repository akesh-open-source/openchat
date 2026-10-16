from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.messaging.application.commands.send_message import SendMessageCommand
from app.messaging.application.services.conversation_membership_guard import (
    ConversationMembershipGuard,
)
from app.messaging.application.services.send_message_service import SendMessageService
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import ConversationNotFoundError
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.domain.entities.outbox_event import MESSAGE_CREATED
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
    InMemoryOutboxRepository,
)


def _service() -> tuple[
    SendMessageService,
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
    InMemoryOutboxRepository,
]:
    memberships = InMemoryMembershipRepository()
    conversations = InMemoryConversationRepository(memberships)
    outbox = InMemoryOutboxRepository()
    messages = InMemoryMessageRepository(conversations, outbox=outbox)
    service = SendMessageService(
        membership_guard=ConversationMembershipGuard(membership_repository=memberships),
        message_repository=messages,
    )
    return service, conversations, memberships, messages, outbox


async def _seed_direct() -> tuple[
    SendMessageService,
    Conversation,
    object,
    object,
    InMemoryOutboxRepository,
]:
    service, conversations, memberships, _messages, outbox = _service()
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
    return service, conversation, user_a, user_b, outbox


def test_send_assigns_contiguous_sequences() -> None:
    async def _run() -> None:
        service, conversation, user_a, _user_b, outbox = await _seed_direct()
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
        assert await outbox.count() == 2
        events = await outbox.list_by_aggregate_id(first.message.id)
        assert events[0].event_type == MESSAGE_CREATED
        assert events[0].published_at is None

    asyncio.run(_run())


def test_send_idempotent_on_client_message_id() -> None:
    async def _run() -> None:
        service, conversation, user_a, _user_b, outbox = await _seed_direct()
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
        # Idempotent retry must not insert a second outbox row.
        assert await outbox.count() == 1

    asyncio.run(_run())


def test_send_rejects_non_member() -> None:
    async def _run() -> None:
        service, conversation, _user_a, _user_b, outbox = await _seed_direct()
        with pytest.raises(ConversationNotFoundError):
            await service.execute(
                SendMessageCommand(
                    user_id=uuid4(),
                    conversation_id=conversation.id,
                    client_message_id="x",
                    body="nope",
                )
            )
        assert await outbox.count() == 0

    asyncio.run(_run())
