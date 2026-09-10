from __future__ import annotations

from fastapi import Request

from app.gateway.config.settings import settings
from app.gateway.exceptions.errors import RateLimitExceededError
from app.gateway.infrastructure.rate_limit.memory_rate_limiter import InMemoryRateLimiter

_limiter = InMemoryRateLimiter()

# Stricter edge limits for abuse-prone public auth paths.
_STRICT_PATHS = frozenset(
    {
        "login",
        "initiate-register",
        "complete-register",
        "forgot-password",
        "reset-password",
    }
)


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip() or "unknown"
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"


def enforce_auth_rate_limit(request: Request, path: str) -> None:
    route = path.split("/", 1)[0]
    if route in _STRICT_PATHS:
        limit = settings.rate_limit_auth_strict_per_window
        scope = f"strict:{route}"
    else:
        limit = settings.rate_limit_auth_default_per_window
        scope = f"default:{route or 'root'}"

    key = f"{scope}:{client_ip(request)}"
    allowed, retry_after = _limiter.check(
        key,
        limit=limit,
        window_seconds=settings.rate_limit_window_seconds,
    )
    if not allowed:
        raise RateLimitExceededError(
            "Rate limit exceeded. Try again later.",
            retry_after=retry_after,
        )
