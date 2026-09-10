from __future__ import annotations

from app.gateway.infrastructure.rate_limit.memory_rate_limiter import InMemoryRateLimiter


def test_in_memory_rate_limiter_allows_then_blocks() -> None:
    limiter = InMemoryRateLimiter()
    assert limiter.check("k", limit=2, window_seconds=60) == (True, 0)
    assert limiter.check("k", limit=2, window_seconds=60) == (True, 0)
    allowed, retry_after = limiter.check("k", limit=2, window_seconds=60)
    assert allowed is False
    assert retry_after >= 1


def test_in_memory_rate_limiter_is_per_key() -> None:
    limiter = InMemoryRateLimiter()
    assert limiter.check("a", limit=1, window_seconds=60)[0] is True
    assert limiter.check("b", limit=1, window_seconds=60)[0] is True
    assert limiter.check("a", limit=1, window_seconds=60)[0] is False
