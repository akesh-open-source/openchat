from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.exceptions.handlers import register_exception_handlers
from app.auth.presentation.http import dependencies as deps
from app.auth.presentation.http import rate_limit as rate_limit_mod
from app.auth.presentation.http.routes import router


@pytest.fixture
def login_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def initiate_register_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def complete_register_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def refresh_token_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def logout_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def change_password_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def list_devices_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def list_sessions_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def revoke_session_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def forgot_password_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def reset_password_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def current_user_id():
    return uuid4()


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    login_service: MagicMock,
    initiate_register_service: MagicMock,
    complete_register_service: MagicMock,
    refresh_token_service: MagicMock,
    logout_service: MagicMock,
    change_password_service: MagicMock,
    list_devices_service: MagicMock,
    list_sessions_service: MagicMock,
    revoke_session_service: MagicMock,
    forgot_password_service: MagicMock,
    reset_password_service: MagicMock,
    current_user_id,
) -> TestClient:
    async def _allow(*_args: Any, **_kwargs: Any) -> tuple[bool, int]:
        return True, 0

    monkeypatch.setattr(rate_limit_mod, "get_redis", lambda: object())
    monkeypatch.setattr(rate_limit_mod.RedisRateLimiter, "check", _allow)

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)

    app.dependency_overrides[deps.get_login_service] = lambda: login_service
    app.dependency_overrides[deps.get_initiate_register_service] = (
        lambda: initiate_register_service
    )
    app.dependency_overrides[deps.get_complete_register_service] = (
        lambda: complete_register_service
    )
    app.dependency_overrides[deps.get_refresh_token_service] = (
        lambda: refresh_token_service
    )
    app.dependency_overrides[deps.get_logout_service] = lambda: logout_service
    app.dependency_overrides[deps.get_change_password_service] = (
        lambda: change_password_service
    )
    app.dependency_overrides[deps.get_list_devices_service] = (
        lambda: list_devices_service
    )
    app.dependency_overrides[deps.get_list_sessions_service] = (
        lambda: list_sessions_service
    )
    app.dependency_overrides[deps.get_revoke_session_service] = (
        lambda: revoke_session_service
    )
    app.dependency_overrides[deps.get_forgot_password_service] = (
        lambda: forgot_password_service
    )
    app.dependency_overrides[deps.get_reset_password_service] = (
        lambda: reset_password_service
    )
    app.dependency_overrides[deps.get_current_user_id] = lambda: current_user_id

    with TestClient(app) as test_client:
        yield test_client
