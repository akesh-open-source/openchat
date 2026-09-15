from __future__ import annotations

import pytest
from fastapi import Request

from app.gateway.exceptions.errors import RateLimitExceededError
from app.gateway.security import rate_limit as rate_limit_mod


def _request(*, forwarded: str | None = None, host: str | None = "127.0.0.1") -> Request:
    headers = []
    if forwarded is not None:
        headers.append((b"x-forwarded-for", forwarded.encode()))
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/auth/login",
        "headers": headers,
        "client": (host, 12345) if host else None,
    }
    return Request(scope)


@pytest.fixture(autouse=True)
def _fresh_limiter(monkeypatch) -> None:
    from app.gateway.infrastructure.rate_limit.memory_rate_limiter import (
        InMemoryRateLimiter,
    )

    monkeypatch.setattr(rate_limit_mod, "_limiter", InMemoryRateLimiter())
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_auth_strict_per_window", 2)
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_auth_default_per_window", 3)
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_window_seconds", 60)


def test_client_ip_from_forwarded_for() -> None:
    request = _request(forwarded="203.0.113.1, 10.0.0.1")
    assert rate_limit_mod.client_ip(request) == "203.0.113.1"


def test_client_ip_from_client_host() -> None:
    request = _request()
    assert rate_limit_mod.client_ip(request) == "127.0.0.1"


def test_enforce_strict_path_blocks() -> None:
    request = _request()
    rate_limit_mod.enforce_auth_rate_limit(request, "login")
    rate_limit_mod.enforce_auth_rate_limit(request, "login")
    with pytest.raises(RateLimitExceededError) as exc:
        rate_limit_mod.enforce_auth_rate_limit(request, "login")
    assert exc.value.retry_after >= 1


def test_enforce_default_path_uses_higher_limit() -> None:
    request = _request()
    for _ in range(3):
        rate_limit_mod.enforce_auth_rate_limit(request, "refresh")
    with pytest.raises(RateLimitExceededError):
        rate_limit_mod.enforce_auth_rate_limit(request, "refresh")


def test_public_auth_paths_constant() -> None:
    from app.gateway.presentation.http.routes.proxy import PUBLIC_AUTH_PATHS

    assert "login" in PUBLIC_AUTH_PATHS
    assert "logout" in PUBLIC_AUTH_PATHS
    assert "change-password" not in PUBLIC_AUTH_PATHS
