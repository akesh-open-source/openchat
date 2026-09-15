from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.messaging.application.commands.get_or_create_direct_conversation import (
    GetOrCreateDirectConversationCommand,
)
from app.messaging.application.services.get_or_create_direct_conversation_service import (
    GetOrCreateDirectConversationService,
)
from app.messaging.domain.exceptions import SelfConversationError
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
)


def test_get_or_create_direct_is_idempotent() -> None:
    async def _run() -> None:
        conversations = InMemoryConversationRepository()
        memberships = InMemoryMembershipRepository()
        service = GetOrCreateDirectConversationService(
            conversation_repository=conversations,
            membership_repository=memberships,
        )
        user_id = uuid4()
        peer_id = uuid4()
        command = GetOrCreateDirectConversationCommand(
            user_id=user_id,
            peer_user_id=peer_id,
        )

        first = await service.execute(command)
        assert first.created is True
        assert len(await memberships.list_by_conversation(first.conversation.id)) == 2

        second = await service.execute(command)
        assert second.created is False
        assert second.conversation.id == first.conversation.id
        assert len(conversations._by_id) == 1

        # Order of participants does not matter.
        swapped = await service.execute(
            GetOrCreateDirectConversationCommand(
                user_id=peer_id,
                peer_user_id=user_id,
            )
        )
        assert swapped.created is False
        assert swapped.conversation.id == first.conversation.id

    asyncio.run(_run())


def test_get_or_create_direct_rejects_self() -> None:
    async def _run() -> None:
        service = GetOrCreateDirectConversationService(
            conversation_repository=InMemoryConversationRepository(),
            membership_repository=InMemoryMembershipRepository(),
        )
        user_id = uuid4()
        with pytest.raises(SelfConversationError):
            await service.execute(
                GetOrCreateDirectConversationCommand(
                    user_id=user_id,
                    peer_user_id=user_id,
                )
            )

    asyncio.run(_run())
