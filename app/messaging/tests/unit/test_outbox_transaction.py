from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.entities.message import Message
from app.messaging.domain.entities.outbox_event import MESSAGE_CREATED, OutboxEvent
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.infrastructure.persistence.postgres.base import Base
from app.messaging.infrastructure.persistence.postgres.mappers.conversation_mapper import (
    to_model as conversation_to_model,
)
from app.messaging.infrastructure.persistence.postgres.mappers.message_mapper import (
    to_model as message_to_model,
)
from app.messaging.infrastructure.persistence.postgres.mappers.outbox_event_mapper import (
    to_model as outbox_to_model,
)
from app.messaging.infrastructure.persistence.postgres.models.message import MessageModel
from app.messaging.infrastructure.persistence.postgres.models.outbox_event import (
    OutboxEventModel,
)
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
    InMemoryOutboxRepository,
)


def _sqlite_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    # Import models so metadata is complete.
    from app.messaging.infrastructure.persistence.postgres.models import (  # noqa: F401
        ConversationModel,
        MembershipModel,
        MessageModel,
        OutboxEventModel,
    )

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def test_message_and_outbox_rollback_leaves_no_orphans() -> None:
    """Same-txn write: rollback removes both message and outbox rows."""
    session = _sqlite_session()
    user_a = uuid4()
    user_b = uuid4()
    conversation = Conversation.create_direct(user_a_id=user_a, user_b_id=user_b)
    session.add(conversation_to_model(conversation))
    session.commit()

    message = Message.create(
        conversation_id=conversation.id,
        sender_id=user_a,
        client_message_id="txn-1",
        sequence=1,
        body="hello",
    )
    event = OutboxEvent.for_message_created(message)

    try:
        session.add(message_to_model(message))
        session.add(outbox_to_model(event))
        session.flush()
        assert session.execute(select(MessageModel)).scalars().first() is not None
        assert session.execute(select(OutboxEventModel)).scalars().first() is not None
        raise RuntimeError("force rollback")
    except RuntimeError:
        session.rollback()

    assert session.execute(select(MessageModel)).scalars().first() is None
    assert session.execute(select(OutboxEventModel)).scalars().first() is None


def test_message_and_outbox_commit_persists_both() -> None:
    session = _sqlite_session()
    user_a = uuid4()
    user_b = uuid4()
    conversation = Conversation.create_direct(user_a_id=user_a, user_b_id=user_b)
    session.add(conversation_to_model(conversation))
    session.commit()

    message = Message.create(
        conversation_id=conversation.id,
        sender_id=user_a,
        client_message_id="ok-1",
        sequence=1,
        body="persisted",
    )
    event = OutboxEvent.for_message_created(message)
    session.add(message_to_model(message))
    session.add(outbox_to_model(event))
    session.commit()

    stored_message = session.execute(select(MessageModel)).scalars().one()
    stored_event = session.execute(select(OutboxEventModel)).scalars().one()
    assert stored_message.id == message.id
    assert stored_event.event_type == MESSAGE_CREATED
    assert stored_event.aggregate_id == message.id
    assert stored_event.published_at is None


def test_inmemory_create_writes_outbox_and_rollback_clears_both() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
        outbox = InMemoryOutboxRepository()
        messages = InMemoryMessageRepository(conversations, outbox=outbox)

        user_a = uuid4()
        user_b = uuid4()
        conversation = Conversation.create_direct(user_a_id=user_a, user_b_id=user_b)
        await conversations.save(conversation)
        await memberships.save(
            Membership.create(
                conversation_id=conversation.id,
                user_id=user_a,
                role=MembershipRole.MEMBER,
            )
        )

        outbox.begin()
        message_snapshot = dict(messages._by_id)
        try:
            messages._fail_after_message = True
            with pytest.raises(RuntimeError, match="forced send failure"):
                await messages.create_with_next_sequence(
                    conversation_id=conversation.id,
                    sender_id=user_a,
                    client_message_id="boom",
                    body="nope",
                )
        finally:
            messages._by_id = message_snapshot
            outbox.rollback()

        assert await messages.get_by_client_message_id(conversation.id, "boom") is None
        assert await outbox.count() == 0

        messages._fail_after_message = False
        outbox.begin()
        created = await messages.create_with_next_sequence(
            conversation_id=conversation.id,
            sender_id=user_a,
            client_message_id="ok",
            body="yes",
        )
        outbox.commit()

        # Sequence may have advanced on the failed attempt (in-memory lock);
        # orphans are what this test guards against.
        assert created.client_message_id == "ok"
        assert await messages.get_by_client_message_id(conversation.id, "boom") is None
        events = await outbox.list_by_aggregate_id(created.id)
        assert len(events) == 1
        assert events[0].event_type == MESSAGE_CREATED
        assert events[0].published_at is None

    asyncio.run(_run())
