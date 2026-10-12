from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.messaging.application.commands.get_or_create_direct_conversation import (
    GetOrCreateDirectConversationCommand,
)
from app.messaging.application.services.get_or_create_direct_conversation_service import (
    GetOrCreateDirectConversationService,
)
from app.messaging.domain.exceptions import PeerNotFoundError, SelfConversationError
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
)


def _service(*, users_client: MagicMock) -> GetOrCreateDirectConversationService:
    return GetOrCreateDirectConversationService(
        conversation_repository=InMemoryConversationRepository(),
        membership_repository=InMemoryMembershipRepository(),
        users_client=users_client,
    )


def test_get_or_create_direct_is_idempotent() -> None:
    async def _run() -> None:
        users_client = MagicMock()
        users_client.user_exists = AsyncMock(return_value=True)
        conversations = InMemoryConversationRepository()
        memberships = InMemoryMembershipRepository()
        service = GetOrCreateDirectConversationService(
            conversation_repository=conversations,
            membership_repository=memberships,
            users_client=users_client,
        )
        user_id = uuid4()
        peer_id = uuid4()
        command = GetOrCreateDirectConversationCommand(
            user_id=user_id,
            peer_user_id=peer_id,
            access_token="test-token",
        )

        first = await service.execute(command)
        assert first.created is True
        assert len(await memberships.list_by_conversation(first.conversation.id)) == 2

        second = await service.execute(command)
        assert second.created is False
        assert second.conversation.id == first.conversation.id
        assert len(conversations._by_id) == 1

        users_client.user_exists.assert_awaited()

    asyncio.run(_run())


def test_get_or_create_direct_rejects_unknown_peer() -> None:
    async def _run() -> None:
        users_client = MagicMock()
        users_client.user_exists = AsyncMock(return_value=False)
        service = _service(users_client=users_client)
        with pytest.raises(PeerNotFoundError):
            await service.execute(
                GetOrCreateDirectConversationCommand(
                    user_id=uuid4(),
                    peer_user_id=uuid4(),
                    access_token="test-token",
                )
            )

    asyncio.run(_run())


def test_get_or_create_direct_rejects_self() -> None:
    async def _run() -> None:
        users_client = MagicMock()
        users_client.user_exists = AsyncMock(return_value=True)
        service = _service(users_client=users_client)
        user_id = uuid4()
        with pytest.raises(SelfConversationError):
            await service.execute(
                GetOrCreateDirectConversationCommand(
                    user_id=user_id,
                    peer_user_id=user_id,
                    access_token="test-token",
                )
            )

    asyncio.run(_run())
