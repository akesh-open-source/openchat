from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from app.gateway.config import settings as settings_mod
from app.gateway.exceptions.handlers import register_exception_handlers
from app.gateway.infrastructure.rate_limit.memory_rate_limiter import InMemoryRateLimiter
from app.gateway.presentation.http import dependencies as deps
from app.gateway.presentation.http.routes import router
from app.gateway.presentation.http.routes import proxy as proxy_mod
from app.gateway.security import authentication as auth_mod
from app.gateway.security import rate_limit as rate_limit_mod


@pytest.fixture(autouse=True)
def _reset_gateway_auth_cache() -> None:
    auth_mod._public_key = None
    yield
    auth_mod._public_key = None


@pytest.fixture
def upstream_response() -> Response:
    return Response(200, json={"ok": True}, headers={"content-type": "application/json"})


@pytest.fixture
def upstream_client(upstream_response: Response) -> MagicMock:
    client = MagicMock()
    client.request = AsyncMock(return_value=upstream_response)
    return client


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    rsa_pem_pair,
    upstream_client: MagicMock,
) -> TestClient:
    monkeypatch.setattr(auth_mod, "_public_key", rsa_pem_pair.public_pem)
    monkeypatch.setattr(auth_mod.settings, "jwt_algorithm", "RS256")
    monkeypatch.setattr(rate_limit_mod, "_limiter", InMemoryRateLimiter())
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_auth_strict_per_window", 100)
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_auth_default_per_window", 100)
    monkeypatch.setattr(rate_limit_mod.settings, "rate_limit_window_seconds", 60)
    monkeypatch.setattr(proxy_mod.settings, "auth_service_url", "http://auth.test")
    monkeypatch.setattr(proxy_mod.settings, "users_service_url", "http://users.test")
    monkeypatch.setattr(settings_mod.settings, "auth_service_url", "http://auth.test")
    monkeypatch.setattr(settings_mod.settings, "users_service_url", "http://users.test")

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_upstream_client] = lambda: upstream_client

    with TestClient(app) as test_client:
        yield test_client
