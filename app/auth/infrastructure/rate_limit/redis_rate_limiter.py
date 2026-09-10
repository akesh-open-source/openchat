from __future__ import annotations

from redis.asyncio import Redis


class RedisRateLimiter:
    """Fixed-window counter rate limiter backed by Redis."""

    def __init__(self, redis: Redis, *, key_prefix: str = "auth:ratelimit") -> None:
        self._redis = redis
        self._prefix = key_prefix

    async def check(
        self,
        key: str,
        *,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds)."""
        full_key = f"{self._prefix}:{key}"
        count = await self._redis.incr(full_key)
        if count == 1:
            await self._redis.expire(full_key, window_seconds)
        if count > limit:
            ttl = await self._redis.ttl(full_key)
            return False, max(int(ttl), 1)
        return True, 0
