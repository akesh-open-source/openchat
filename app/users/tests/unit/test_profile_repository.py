from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import pytest

from app.users.domain.entities.profile import Profile
from app.users.domain.value_objects.display_name import DisplayName


class InMemoryProfileRepository:
    """Fake ProfileRepository for contract tests (no Postgres)."""

    def __init__(self) -> None:
        self._items: dict[UUID, Profile] = {}

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        return self._items.get(user_id)

    async def get_by_email(self, email: str) -> Profile | None:
        normalized = email.strip().lower()
        for profile in self._items.values():
            if profile.email == normalized:
                return profile
        return None

    async def save(self, profile: Profile) -> None:
        self._items[profile.user_id] = profile

    async def delete(self, user_id: UUID) -> None:
        self._items.pop(user_id, None)


def test_profile_repository_save_get_delete_contract() -> None:
    async def _run() -> None:
        repo = InMemoryProfileRepository()
        user_id = uuid4()
        profile = Profile.create(
            user_id=user_id,
            display_name=DisplayName("Alice"),
            email="alice@example.com",
        )

        assert await repo.get_by_user_id(user_id) is None

        await repo.save(profile)
        loaded = await repo.get_by_user_id(user_id)
        assert loaded is not None
        assert loaded.user_id == user_id
        assert loaded.display_name.value == "Alice"

        by_email = await repo.get_by_email("  Alice@Example.COM ")
        assert by_email is not None
        assert by_email.user_id == user_id

        profile.update_display_name(DisplayName("Alice Updated"))
        await repo.save(profile)
        updated = await repo.get_by_user_id(user_id)
        assert updated is not None
        assert updated.display_name.value == "Alice Updated"

        await repo.delete(user_id)
        assert await repo.get_by_user_id(user_id) is None

    asyncio.run(_run())
