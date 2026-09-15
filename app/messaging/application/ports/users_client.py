from __future__ import annotations

from typing import Protocol
from uuid import UUID


class UsersClient(Protocol):
    """Port for calling the users service (Compose-internal HTTP)."""

    async def user_exists(
        self,
        *,
        user_id: UUID,
        access_token: str,
    ) -> bool:
        """Return True if a profile exists for user_id; False on 404.

        Raises UsersUnavailableError (or equivalent) when users cannot be reached
        or returns an unexpected error.
        """
        ...
