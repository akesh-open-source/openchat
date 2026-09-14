from __future__ import annotations

import logging
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)


class HttpxUsersClient:
    """HTTP adapter for the users service internal API."""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def create_profile(
        self,
        *,
        user_id: UUID,
        display_name: str,
        email: str | None = None,
    ) -> None:
        url = f"{self._base_url}/internal/profiles"
        payload: dict[str, object] = {
            "user_id": str(user_id),
            "display_name": display_name,
        }
        if email is not None:
            payload["email"] = email

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info(
                "Synced profile to users service user_id=%s created=%s",
                user_id,
                response.json().get("created"),
            )
