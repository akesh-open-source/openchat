from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.users.domain.entities.profile import Profile


class ProfileRepository(Protocol):
    """Port for profile persistence."""

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        """Return the profile for the given auth user id, or None."""
        ...

    async def get_by_email(self, email: str) -> Profile | None:
        """Return the profile with the given normalized email, or None."""
        ...

    async def save(self, profile: Profile) -> None:
        """Persist a new profile or update an existing one (upsert)."""
        ...

    async def delete(self, user_id: UUID) -> None:
        """Remove the profile for the given user id, if present."""
        ...
