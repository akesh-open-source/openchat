from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import ConversationNotFoundError
from app.messaging.tests.unit.test_repositories import InMemoryConversationRepository


def test_allocate_next_sequence_persists_bump_on_conversation() -> None:
    async def _run() -> None:
        repo = InMemoryConversationRepository()
        conversation = Conversation.create_direct(
            user_a_id=uuid4(),
            user_b_id=uuid4(),
        )
        await repo.save(conversation)

        first = await repo.allocate_next_sequence(conversation.id)
        second = await repo.allocate_next_sequence(conversation.id)

        assert first == 1
        assert second == 2
        loaded = await repo.get_by_id(conversation.id)
        assert loaded is not None
        assert loaded.next_sequence == 2

    asyncio.run(_run())


def test_allocate_next_sequence_missing_conversation() -> None:
    async def _run() -> None:
        repo = InMemoryConversationRepository()
        with pytest.raises(ConversationNotFoundError):
            await repo.allocate_next_sequence(uuid4())

    asyncio.run(_run())


def test_concurrent_allocate_next_sequence_is_unique_and_contiguous() -> None:
    async def _run() -> None:
        repo = InMemoryConversationRepository()
        conversation = Conversation.create_direct(
            user_a_id=uuid4(),
            user_b_id=uuid4(),
        )
        await repo.save(conversation)

        count = 50
        sequences = await asyncio.gather(
            *[repo.allocate_next_sequence(conversation.id) for _ in range(count)]
        )

        assert sorted(sequences) == list(range(1, count + 1))
        assert len(set(sequences)) == count

        loaded = await repo.get_by_id(conversation.id)
        assert loaded is not None
        assert loaded.next_sequence == count

    asyncio.run(_run())


def test_concurrent_allocation_assigns_message_sequences_without_collision() -> None:
    async def _run() -> None:
        repo = InMemoryConversationRepository()
        conversation = Conversation.create_direct(
            user_a_id=uuid4(),
            user_b_id=uuid4(),
        )
        await repo.save(conversation)
        sender_id = conversation.direct_user_a_id
        assert sender_id is not None

        async def _send(index: int) -> Message:
            sequence = await repo.allocate_next_sequence(conversation.id)
            return Message.create(
                conversation_id=conversation.id,
                sender_id=sender_id,
                client_message_id=f"client-{index}",
                sequence=sequence,
                body=f"msg-{index}",
            )

        messages = await asyncio.gather(*[_send(i) for i in range(20)])
        sequences = [message.sequence for message in messages]
        assert sorted(sequences) == list(range(1, 21))
        assert len({message.client_message_id for message in messages}) == 20

    asyncio.run(_run())


def test_sequence_locks_are_independent_per_conversation() -> None:
    async def _run() -> None:
        repo = InMemoryConversationRepository()
        first = Conversation.create_direct(user_a_id=uuid4(), user_b_id=uuid4())
        second = Conversation.create_direct(user_a_id=uuid4(), user_b_id=uuid4())
        await repo.save(first)
        await repo.save(second)

        results = await asyncio.gather(
            repo.allocate_next_sequence(first.id),
            repo.allocate_next_sequence(second.id),
            repo.allocate_next_sequence(first.id),
            repo.allocate_next_sequence(second.id),
        )
        # Each conversation has its own counter starting at 1.
        assert sorted(results[0::2]) == [1, 2]
        assert sorted(results[1::2]) == [1, 2]

    asyncio.run(_run())
