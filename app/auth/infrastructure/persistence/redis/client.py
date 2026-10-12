from __future__ import annotations

from redis.asyncio import Redis

from app.auth.config.settings import settings

_redis_client: Redis | None = None


async def init_redis() -> Redis:
    global _redis_client
    _redis_client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    await _redis_client.ping()
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def get_redis() -> Redis:
    if _redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return _redis_client
