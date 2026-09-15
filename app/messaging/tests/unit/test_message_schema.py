from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import DomainError, MessageAlreadyExistsError
from app.messaging.domain.value_objects.message_status import MessageStatus
from app.messaging.tests.unit.test_repositories import InMemoryMessageRepository


def test_allocate_next_sequence_starts_at_one_and_is_monotonic() -> None:
    conversation = Conversation.create_direct(
        user_a_id=uuid4(),
        user_b_id=uuid4(),
    )
    assert conversation.next_sequence == 0

    assert conversation.allocate_next_sequence() == 1
    assert conversation.next_sequence == 1
    assert conversation.allocate_next_sequence() == 2
    assert conversation.allocate_next_sequence() == 3
    assert conversation.next_sequence == 3


def test_allocate_next_sequence_feeds_message_create() -> None:
    conversation = Conversation.create_direct(
        user_a_id=uuid4(),
        user_b_id=uuid4(),
    )
    sender_id = conversation.direct_user_a_id
    assert sender_id is not None

    sequence = conversation.allocate_next_sequence()
    message = Message.create(
        conversation_id=conversation.id,
        sender_id=sender_id,
        client_message_id="phone-1",
        sequence=sequence,
        body="hello",
    )
    assert message.sequence == 1
    assert message.status is MessageStatus.SENT
    assert conversation.next_sequence == 1


def test_message_create_rejects_empty_client_message_id() -> None:
    with pytest.raises(DomainError, match="client_message_id"):
        Message.create(
            conversation_id=uuid4(),
            sender_id=uuid4(),
            client_message_id="   ",
            sequence=1,
            body="hi",
        )


def test_message_create_rejects_non_positive_sequence() -> None:
    with pytest.raises(DomainError, match="sequence"):
        Message.create(
            conversation_id=uuid4(),
            sender_id=uuid4(),
            client_message_id="c1",
            sequence=0,
            body="hi",
        )


def test_message_create_rejects_empty_body() -> None:
    with pytest.raises(DomainError, match="body"):
        Message.create(
            conversation_id=uuid4(),
            sender_id=uuid4(),
            client_message_id="c1",
            sequence=1,
            body="",
        )


def test_message_repository_rejects_duplicate_client_message_id() -> None:
    async def _run() -> None:
        repo = InMemoryMessageRepository()
        conversation_id = uuid4()
        first = Message.create(
            conversation_id=conversation_id,
            sender_id=uuid4(),
            client_message_id="same-client-id",
            sequence=1,
            body="one",
        )
        duplicate = Message.create(
            conversation_id=conversation_id,
            sender_id=uuid4(),
            client_message_id="same-client-id",
            sequence=2,
            body="two",
        )
        await repo.save(first)
        with pytest.raises(MessageAlreadyExistsError):
            await repo.save(duplicate)

    asyncio.run(_run())


def test_message_repository_rejects_duplicate_sequence() -> None:
    async def _run() -> None:
        repo = InMemoryMessageRepository()
        conversation_id = uuid4()
        first = Message.create(
            conversation_id=conversation_id,
            sender_id=uuid4(),
            client_message_id="c1",
            sequence=1,
            body="one",
        )
        duplicate = Message.create(
            conversation_id=conversation_id,
            sender_id=uuid4(),
            client_message_id="c2",
            sequence=1,
            body="two",
        )
        await repo.save(first)
        with pytest.raises(MessageAlreadyExistsError):
            await repo.save(duplicate)

    asyncio.run(_run())


def test_message_uniqueness_is_scoped_per_conversation() -> None:
    async def _run() -> None:
        repo = InMemoryMessageRepository()
        conversation_a = uuid4()
        conversation_b = uuid4()
        await repo.save(
            Message.create(
                conversation_id=conversation_a,
                sender_id=uuid4(),
                client_message_id="shared-client-id",
                sequence=1,
                body="a",
            )
        )
        # Same client_message_id / sequence in another conversation is fine.
        await repo.save(
            Message.create(
                conversation_id=conversation_b,
                sender_id=uuid4(),
                client_message_id="shared-client-id",
                sequence=1,
                body="b",
            )
        )
        latest = await repo.get_latest_by_conversation_ids(
            [conversation_a, conversation_b],
        )
        assert latest[conversation_a].body == "a"
        assert latest[conversation_b].body == "b"

    asyncio.run(_run())
