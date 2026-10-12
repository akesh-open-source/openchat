from __future__ import annotations

import time
from threading import Lock


class InMemoryRateLimiter:
    """Fixed-window rate limiter for a single gateway process."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._windows: dict[str, tuple[int, float]] = {}

    def check(
        self,
        key: str,
        *,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        now = time.monotonic()
        with self._lock:
            count, started = self._windows.get(key, (0, now))
            if now - started >= window_seconds:
                count, started = 0, now
            count += 1
            self._windows[key] = (count, started)
            if count > limit:
                retry_after = max(int(window_seconds - (now - started)), 1)
                return False, retry_after
            return True, 0
