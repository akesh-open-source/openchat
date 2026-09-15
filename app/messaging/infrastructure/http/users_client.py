from __future__ import annotations

import asyncio
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
        profile = await self._lookup(user_id=user_id, access_token=access_token)
        return profile is not None

    async def get_display_names(
        self,
        *,
        user_ids: list[UUID],
        access_token: str,
    ) -> dict[UUID, str]:
        unique_ids = list(dict.fromkeys(user_ids))
        if not unique_ids:
            return {}

        results = await asyncio.gather(
            *[
                self._lookup(user_id=user_id, access_token=access_token)
                for user_id in unique_ids
            ]
        )
        names: dict[UUID, str] = {}
        for user_id, profile in zip(unique_ids, results, strict=True):
            if profile is not None:
                names[user_id] = profile
        return names

    async def _lookup(
        self,
        *,
        user_id: UUID,
        access_token: str,
    ) -> str | None:
        """Return display_name if found, None on 404."""
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
            return None
        if response.status_code == 200:
            payload = response.json()
            display_name = payload.get("display_name")
            if not isinstance(display_name, str) or not display_name.strip():
                raise UsersUnavailableError("users lookup returned invalid display_name")
            return display_name

        logger.warning(
            "Users lookup unexpected status user_id=%s status=%s",
            user_id,
            response.status_code,
        )
        raise UsersUnavailableError(
            f"users service returned {response.status_code}"
        )
