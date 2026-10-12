from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

from app.messaging.application.dto.conversation_list_cursor import ConversationListCursor
from app.messaging.application.dto.message_list_cursor import MessageListCursor
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import (
    ConversationNotFoundError,
    MessageAlreadyExistsError,
)
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.domain.value_objects.user_pair import sorted_user_pair


class InMemoryMembershipRepository:
    """Fake MembershipRepository for contract tests (no Postgres)."""

    def __init__(self) -> None:
        self._items: dict[tuple[UUID, UUID], Membership] = {}

    async def get(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Membership | None:
        return self._items.get((conversation_id, user_id))

    async def list_by_conversation(self, conversation_id: UUID) -> list[Membership]:
        return [
            membership
            for (cid, _), membership in self._items.items()
            if cid == conversation_id
        ]

    async def list_by_user(self, user_id: UUID) -> list[Membership]:
        return [
            membership
            for (_, uid), membership in self._items.items()
            if uid == user_id
        ]

    async def save(self, membership: Membership) -> None:
        self._items[(membership.conversation_id, membership.user_id)] = membership

    async def save_many(self, memberships: list[Membership]) -> None:
        for membership in memberships:
            await self.save(membership)


class InMemoryConversationRepository:
    """Fake ConversationRepository for contract tests (no Postgres)."""

    def __init__(
        self,
        memberships: InMemoryMembershipRepository | None = None,
    ) -> None:
        self._by_id: dict[UUID, Conversation] = {}
        self._memberships = memberships
        # Per-conversation locks simulate Postgres FOR UPDATE serialization.
        self._sequence_locks: dict[UUID, asyncio.Lock] = {}

    def _lock_for(self, conversation_id: UUID) -> asyncio.Lock:
        lock = self._sequence_locks.get(conversation_id)
        if lock is None:
            lock = asyncio.Lock()
            self._sequence_locks[conversation_id] = lock
        return lock

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        return self._by_id.get(conversation_id)

    async def get_direct_between(
        self,
        user_a_id: UUID,
        user_b_id: UUID,
    ) -> Conversation | None:
        user_a, user_b = sorted_user_pair(user_a_id, user_b_id)
        for conversation in self._by_id.values():
            if (
                conversation.is_direct
                and conversation.direct_user_a_id == user_a
                and conversation.direct_user_b_id == user_b
            ):
                return conversation
        return None

    async def list_for_user(
        self,
        user_id: UUID,
        *,
        limit: int,
        cursor: ConversationListCursor | None = None,
    ) -> list[Conversation]:
        if self._memberships is None:
            raise RuntimeError(
                "InMemoryConversationRepository requires memberships for list_for_user"
            )
        member_ids = {
            membership.conversation_id
            for membership in await self._memberships.list_by_user(user_id)
        }
        items = [
            conversation
            for conversation_id, conversation in self._by_id.items()
            if conversation_id in member_ids
        ]
        items.sort(key=lambda c: (c.updated_at, c.id), reverse=True)
        if cursor is not None:
            items = [
                conversation
                for conversation in items
                if (conversation.updated_at, conversation.id)
                < (cursor.updated_at, cursor.id)
            ]
        return items[:limit]

    async def save(self, conversation: Conversation) -> None:
        self._by_id[conversation.id] = conversation

    async def allocate_next_sequence(self, conversation_id: UUID) -> int:
        async with self._lock_for(conversation_id):
            conversation = self._by_id.get(conversation_id)
            if conversation is None:
                raise ConversationNotFoundError("Conversation not found")
            # Yield so concurrent waiters can contend on the lock (stresses serialization).
            await asyncio.sleep(0)
            return conversation.allocate_next_sequence()


class InMemoryMessageRepository:
    """Fake MessageRepository for contract tests (no Postgres)."""

    def __init__(
        self,
        conversations: InMemoryConversationRepository | None = None,
    ) -> None:
        self._by_id: dict[UUID, Message] = {}
        self._conversations = conversations

    async def get_latest_by_conversation_ids(
        self,
        conversation_ids: list[UUID],
    ) -> dict[UUID, Message]:
        latest: dict[UUID, Message] = {}
        wanted = set(conversation_ids)
        for message in self._by_id.values():
            if message.conversation_id not in wanted:
                continue
            current = latest.get(message.conversation_id)
            if current is None or message.sequence > current.sequence:
                latest[message.conversation_id] = message
        return latest

    async def get_by_client_message_id(
        self,
        conversation_id: UUID,
        client_message_id: str,
    ) -> Message | None:
        for message in self._by_id.values():
            if (
                message.conversation_id == conversation_id
                and message.client_message_id == client_message_id
            ):
                return message
        return None

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        limit: int,
        cursor: MessageListCursor | None = None,
    ) -> list[Message]:
        items = [
            message
            for message in self._by_id.values()
            if message.conversation_id == conversation_id
        ]
        items.sort(key=lambda m: m.sequence)
        if cursor is not None:
            items = [message for message in items if message.sequence > cursor.sequence]
        return items[:limit]

    async def create_with_next_sequence(
        self,
        *,
        conversation_id: UUID,
        sender_id: UUID,
        client_message_id: str,
        body: str,
    ) -> Message:
        if self._conversations is None:
            raise RuntimeError(
                "InMemoryMessageRepository requires conversations for "
                "create_with_next_sequence"
            )
        sequence = await self._conversations.allocate_next_sequence(conversation_id)
        message = Message.create(
            conversation_id=conversation_id,
            sender_id=sender_id,
            client_message_id=client_message_id,
            sequence=sequence,
            body=body,
        )
        await self.save(message)
        return message

    async def save(self, message: Message) -> None:
        for existing in self._by_id.values():
            if existing.conversation_id != message.conversation_id:
                continue
            if existing.client_message_id == message.client_message_id:
                raise MessageAlreadyExistsError(
                    "Message already exists for this client_message_id"
                )
            if existing.sequence == message.sequence:
                raise MessageAlreadyExistsError(
                    "Message already exists for this sequence"
                )
        self._by_id[message.id] = message


def test_conversation_and_membership_repository_contract() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)

        user_a = uuid4()
        user_b = uuid4()
        conversation = Conversation.create_direct(user_a_id=user_a, user_b_id=user_b)

        assert await conversations.get_by_id(conversation.id) is None
        await conversations.save(conversation)

        loaded = await conversations.get_by_id(conversation.id)
        assert loaded is not None
        assert loaded.id == conversation.id

        by_pair = await conversations.get_direct_between(user_b, user_a)
        assert by_pair is not None
        assert by_pair.id == conversation.id

        member_a = Membership.create(
            conversation_id=conversation.id,
            user_id=user_a,
            role=MembershipRole.MEMBER,
        )
        member_b = Membership.create(
            conversation_id=conversation.id,
            user_id=user_b,
        )
        await memberships.save_many([member_a, member_b])

        assert await memberships.get(conversation.id, user_a) is not None
        listed = await memberships.list_by_conversation(conversation.id)
        assert {m.user_id for m in listed} == {user_a, user_b}
        assert len(await memberships.list_by_user(user_a)) == 1

        for_user = await conversations.list_for_user(user_a, limit=10)
        assert len(for_user) == 1
        assert for_user[0].id == conversation.id

        messages = InMemoryMessageRepository()
        older = Message.create(
            conversation_id=conversation.id,
            sender_id=user_a,
            client_message_id="c1",
            sequence=1,
            body="first",
        )
        newer = Message.create(
            conversation_id=conversation.id,
            sender_id=user_b,
            client_message_id="c2",
            sequence=2,
            body="second",
        )
        await messages.save(older)
        await messages.save(newer)
        latest = await messages.get_latest_by_conversation_ids([conversation.id])
        assert latest[conversation.id].body == "second"

    asyncio.run(_run())
