from __future__ import annotations

import json

from redis.asyncio import Redis

from app.auth.application.ports.pending_registration_store import PendingRegistration

_KEY_PREFIX = "auth:pending_registration:"


class RedisPendingRegistrationStore:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def _key(self, token: str) -> str:
        return f"{_KEY_PREFIX}{token}"

    async def save(
        self,
        token: str,
        pending: PendingRegistration,
        *,
        ttl_seconds: int,
    ) -> None:
        payload = json.dumps(
            {
                "email": pending.email,
                "password_hash": pending.password_hash,
                "display_name": pending.display_name,
            }
        )
        await self._redis.set(self._key(token), payload, ex=ttl_seconds)

    async def get(self, token: str) -> PendingRegistration | None:
        raw = await self._redis.get(self._key(token))
        if raw is None:
            return None
        data = json.loads(raw)
        return PendingRegistration(
            email=data["email"],
            password_hash=data["password_hash"],
            display_name=data["display_name"],
        )

    async def delete(self, token: str) -> None:
        await self._redis.delete(self._key(token))
