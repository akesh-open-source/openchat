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
        """Return True if a profile exists for user_id; False on 404."""
        ...

    async def get_display_names(
        self,
        *,
        user_ids: list[UUID],
        access_token: str,
    ) -> dict[UUID, str]:
        """Return display_name by user_id for profiles that exist.

        Missing users are omitted. Transient users outages raise
        UsersUnavailableError (callers may choose to soft-fail).
        """
        ...
