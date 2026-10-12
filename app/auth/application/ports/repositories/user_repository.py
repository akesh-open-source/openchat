from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.auth.domain.entities.user import User


class UserRepository(Protocol):
    """Port for user persistence."""

    async def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or None if not found."""
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return the user with the given id, or None if not found."""
        ...

    async def save(self, user: User) -> None:
        """Persist a new user or update an existing one (upsert)."""
        ...

    async def delete(self, user_id: UUID) -> None:
        """Remove the user with the given id, if present."""
        ...
