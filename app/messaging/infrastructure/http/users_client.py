from __future__ import annotations

import logging
from uuid import UUID

import httpx

from app.messaging.domain.exceptions import UsersUnavailableError

logger = logging.getLogger(__name__)


class HttpxUsersClient:
    """HTTP adapter for users public lookup (JWT forwarded from the caller)."""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def user_exists(
        self,
        *,
        user_id: UUID,
        access_token: str,
    ) -> bool:
        url = f"{self._base_url}/users/lookup"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"user_id": str(user_id)}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as exc:
            logger.warning("Users lookup failed user_id=%s error=%s", user_id, exc)
            raise UsersUnavailableError("users service is unavailable") from exc

        if response.status_code == 404:
            return False
        if response.status_code == 200:
            return True

        logger.warning(
            "Users lookup unexpected status user_id=%s status=%s",
            user_id,
            response.status_code,
        )
        raise UsersUnavailableError(
            f"users service returned {response.status_code}"
        )
