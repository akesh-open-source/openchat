from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.domain.value_objects.user_pair import sorted_user_pair


class InMemoryConversationRepository:
    """Fake ConversationRepository for contract tests (no Postgres)."""

    def __init__(self) -> None:
        self._by_id: dict[UUID, Conversation] = {}

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

    async def save(self, conversation: Conversation) -> None:
        self._by_id[conversation.id] = conversation


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


def test_conversation_and_membership_repository_contract() -> None:
    async def _run() -> None:
        conversations = InMemoryConversationRepository()
        memberships = InMemoryMembershipRepository()

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

    asyncio.run(_run())
