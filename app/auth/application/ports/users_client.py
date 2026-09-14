from __future__ import annotations

from typing import Protocol
from uuid import UUID


class UsersClient(Protocol):
    """Port for calling the users service (Compose-internal HTTP)."""

    async def create_profile(
        self,
        *,
        user_id: UUID,
        display_name: str,
        email: str | None = None,
    ) -> None:
        """Create (or idempotently fetch) a profile in the users service."""
        ...
