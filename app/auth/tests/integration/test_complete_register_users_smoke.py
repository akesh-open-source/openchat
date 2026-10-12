from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.application.ports.pending_registration_store import PendingRegistration
from app.auth.application.services.complete_register_service import (
    CompleteRegisterService,
)
from app.auth.exceptions.handlers import register_exception_handlers
from app.auth.presentation.http import dependencies as deps
from app.auth.presentation.http import rate_limit as rate_limit_mod
from app.auth.presentation.http.routes import router


def _pending() -> PendingRegistration:
    return PendingRegistration(
        email="alice@example.com",
        password_hash="hashed-password",
        display_name="Alice",
    )


def _complete_register_service(*, users_client: MagicMock) -> CompleteRegisterService:
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    pending = MagicMock()
    pending.get = AsyncMock(return_value=_pending())
    pending.delete = AsyncMock()
    email_sender = MagicMock()
    email_sender.send = AsyncMock()
    template = MagicMock()
    template.render_register_user = MagicMock(
        return_value=MagicMock(
            subject="Welcome",
            text_body="hi",
            html_body="<p>hi</p>",
        )
    )
    return CompleteRegisterService(
        user_repository=repo,
        pending_store=pending,
        email_sender=email_sender,
        template_renderer=template,
        users_client=users_client,
        app_name="OpenChat",
        login_url="http://localhost/docs",
    )


@pytest.fixture
def users_client() -> MagicMock:
    client = MagicMock()
    client.create_profile = AsyncMock(return_value=None)
    return client


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    users_client: MagicMock,
) -> TestClient:
    async def _allow(*_args: Any, **_kwargs: Any) -> tuple[bool, int]:
        return True, 0

    monkeypatch.setattr(rate_limit_mod, "get_redis", lambda: object())
    monkeypatch.setattr(rate_limit_mod.RedisRateLimiter, "check", _allow)

    service = _complete_register_service(users_client=users_client)
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_complete_register_service] = lambda: service
    app.dependency_overrides[deps.get_current_user_id] = lambda: uuid4()

    with TestClient(app) as test_client:
        yield test_client


def test_complete_register_smokes_users_profile_create(
    client: TestClient,
    users_client: MagicMock,
) -> None:
    """HTTP smoke: complete-register calls users create-profile after auth user save."""
    response = client.post(
        "/auth/complete-register",
        json={"token": "registration-token"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"

    users_client.create_profile.assert_awaited_once()
    kwargs = users_client.create_profile.await_args.kwargs
    assert kwargs["display_name"] == "Alice"
    assert kwargs["email"] == "alice@example.com"
    assert kwargs["user_id"] is not None


def test_complete_register_smokes_when_users_unavailable(
    client: TestClient,
    users_client: MagicMock,
) -> None:
    """HTTP smoke: registration still succeeds if users service is down."""
    users_client.create_profile = AsyncMock(side_effect=httpx.ConnectError("down"))

    response = client.post(
        "/auth/complete-register",
        json={"token": "registration-token"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    users_client.create_profile.assert_awaited_once()
