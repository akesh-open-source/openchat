from __future__ import annotations

import asyncio
from uuid import uuid4

from app.users.application.commands.create_profile import CreateProfileCommand
from app.users.application.services.create_profile_service import CreateProfileService
from app.users.tests.unit.test_profile_repository import InMemoryProfileRepository


def test_create_profile_service_is_idempotent() -> None:
    async def _run() -> None:
        repo = InMemoryProfileRepository()
        service = CreateProfileService(profile_repository=repo)
        user_id = uuid4()
        command = CreateProfileCommand(
            user_id=user_id,
            display_name="Alice",
            email="alice@example.com",
        )

        first = await service.create(command)
        assert first.created is True
        assert first.profile.display_name.value == "Alice"

        second = await service.create(command)
        assert second.created is False
        assert second.profile.user_id == user_id
        assert len(repo._items) == 1

    asyncio.run(_run())
