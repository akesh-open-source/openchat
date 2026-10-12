from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.messaging.application.services.conversation_membership_guard import (
    ConversationMembershipGuard,
)
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import ConversationNotFoundError
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
)


def test_require_member_returns_membership() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
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
        guard = ConversationMembershipGuard(membership_repository=memberships)
        membership = await guard.require_member(
            conversation_id=conversation.id,
            user_id=user_a,
        )
        assert membership.user_id == user_a
        assert membership.conversation_id == conversation.id

    asyncio.run(_run())


def test_require_member_non_member_raises_not_found() -> None:
    async def _run() -> None:
        memberships = InMemoryMembershipRepository()
        conversations = InMemoryConversationRepository(memberships)
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
        guard = ConversationMembershipGuard(membership_repository=memberships)
        with pytest.raises(ConversationNotFoundError):
            await guard.require_member(
                conversation_id=conversation.id,
                user_id=uuid4(),
            )

    asyncio.run(_run())


def test_require_member_unknown_conversation_raises_not_found() -> None:
    async def _run() -> None:
        guard = ConversationMembershipGuard(
            membership_repository=InMemoryMembershipRepository(),
        )
        with pytest.raises(ConversationNotFoundError):
            await guard.require_member(
                conversation_id=uuid4(),
                user_id=uuid4(),
            )

    asyncio.run(_run())
