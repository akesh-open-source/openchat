from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Request

from app.auth.config.settings import settings
from app.auth.domain.exceptions import RateLimitExceededError
from app.auth.infrastructure.persistence.redis.client import get_redis
from app.auth.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip() or "unknown"
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"


def rate_limit(
    scope: str,
    *,
    limit: int | None = None,
    window_seconds: int | None = None,
) -> Callable:
    """Return a FastAPI Depends() that enforces a fixed-window rate limit."""

    async def _dependency(request: Request) -> None:
        lim = (
            limit
            if limit is not None
            else settings.rate_limit_default_per_window
        )
        window = (
            window_seconds
            if window_seconds is not None
            else settings.rate_limit_window_seconds
        )
        limiter = RedisRateLimiter(get_redis())
        key = f"{scope}:{client_ip(request)}"
        allowed, retry_after = await limiter.check(
            key,
            limit=lim,
            window_seconds=window,
        )
        if not allowed:
            raise RateLimitExceededError(
                "Rate limit exceeded. Try again later.",
                retry_after=retry_after,
            )

    return Depends(_dependency)


def limit_login() -> Callable:
    return rate_limit("login", limit=settings.rate_limit_login_per_window)


def limit_register() -> Callable:
    return rate_limit("register", limit=settings.rate_limit_register_per_window)


def limit_password_reset() -> Callable:
    return rate_limit(
        "password-reset",
        limit=settings.rate_limit_password_reset_per_window,
    )


def limit_refresh() -> Callable:
    return rate_limit("refresh", limit=settings.rate_limit_refresh_per_window)


def limit_default() -> Callable:
    return rate_limit("default", limit=settings.rate_limit_default_per_window)
