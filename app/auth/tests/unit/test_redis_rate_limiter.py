from __future__ import annotations

import asyncio
from typing import Any

from app.auth.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter


class FakeRedis:
    def __init__(self) -> None:
        self._counts: dict[str, int] = {}
        self._ttls: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self._counts[key] = self._counts.get(key, 0) + 1
        return self._counts[key]

    async def expire(self, key: str, seconds: int) -> bool:
        self._ttls[key] = seconds
        return True

    async def ttl(self, key: str) -> int:
        return self._ttls.get(key, -1)


def test_redis_rate_limiter_allows_then_blocks() -> None:
    async def _run() -> None:
        redis: Any = FakeRedis()
        limiter = RedisRateLimiter(redis, key_prefix="test")

        allowed, retry = await limiter.check("ip:1", limit=2, window_seconds=60)
        assert allowed is True and retry == 0

        allowed, retry = await limiter.check("ip:1", limit=2, window_seconds=60)
        assert allowed is True and retry == 0

        allowed, retry = await limiter.check("ip:1", limit=2, window_seconds=60)
        assert allowed is False
        assert retry >= 1
        assert redis._ttls["test:ip:1"] == 60

    asyncio.run(_run())
