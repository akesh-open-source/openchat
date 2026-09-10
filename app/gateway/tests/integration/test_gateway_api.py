from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Request, RequestError

from app.gateway.exceptions.handlers import register_exception_handlers
from app.gateway.infrastructure.rate_limit.memory_rate_limiter import InMemoryRateLimiter
from app.gateway.presentation.http import dependencies as deps
from app.gateway.presentation.http.routes import router
from app.gateway.presentation.http.routes import proxy as proxy_mod
from app.gateway.security import authentication as auth_mod
from app.gateway.security import rate_limit as rate_limit_mod


def _access_token(private_pem: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(uuid4()),
            "email": "user@example.com",
            "type": "access",
            "sid": str(uuid4()),
            "iat": now,
            "exp": now + timedelta(minutes=15),
        },
        private_pem,
        algorithm="RS256",
    )


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_proxy_public_login_without_jwt(
    client: TestClient,
    upstream_client: MagicMock,
) -> None:
    response = client.post("/auth/login", json={"email": "a@b.com"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    upstream_client.request.assert_awaited_once()
    call = upstream_client.request.await_args
    assert call.kwargs["url"] == "http://auth.test/auth/login"
    assert call.kwargs["method"] == "POST"


def test_proxy_protected_without_jwt_returns_401(client: TestClient) -> None:
    response = client.post(
        "/auth/change-password",
        json={"current_password": "old", "new_password": "newpass12"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_proxy_protected_with_valid_jwt(
    client: TestClient,
    rsa_pem_pair,
    upstream_client: MagicMock,
) -> None:
    token = _access_token(rsa_pem_pair.private_pem)
    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpassword", "new_password": "newpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    upstream_client.request.assert_awaited_once()


def test_proxy_protected_with_invalid_jwt(client: TestClient) -> None:
    response = client.get(
        "/auth/devices",
        headers={"Authorization": "Bearer not.a.jwt"},
    )
    assert response.status_code == 401


def test_proxy_upstream_unavailable(
    client: TestClient,
    upstream_client: MagicMock,
) -> None:
    upstream_client.request = AsyncMock(
        side_effect=RequestError(
            "boom",
            request=Request("POST", "http://auth.test/auth/login"),
        )
    )
    response = client.post("/auth/login", json={})
    assert response.status_code == 502
    assert "auth" in response.json()["detail"].lower()


def test_proxy_edge_rate_limit(
    monkeypatch: pytest.MonkeyPatch,
    rsa_pem_pair,
    upstream_client: MagicMock,
) -> None:
    monkeypatch.setattr(auth_mod, "_public_key", rsa_pem_pair.public_pem)
    monkeypatch.setattr(auth_mod.settings, "jwt_algorithm", "RS256")
    monkeypatch.setattr(rate_limit_mod, "_limiter", InMemoryRateLimiter())
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_auth_strict_per_window", 1)
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_window_seconds", 60)
    monkeypatch.setattr(proxy_mod.settings, "auth_service_url", "http://auth.test")

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_upstream_client] = lambda: upstream_client

    with TestClient(app) as test_client:
        assert test_client.post("/auth/login", json={}).status_code == 200
        limited = test_client.post("/auth/login", json={})
        assert limited.status_code == 429
        assert "retry-after" in {k.lower() for k in limited.headers.keys()}
