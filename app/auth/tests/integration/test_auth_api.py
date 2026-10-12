from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.auth.application.ports.token_issuer import TokenPair
from app.auth.application.services.initiate_register_service import (
    InitiateRegisterResult,
)
from app.auth.domain.entities.device import Device
from app.auth.domain.entities.session import Session
from app.auth.domain.entities.user import User
from app.auth.domain.exceptions import (
    InvalidCredentialsError,
    SessionNotFoundError,
    UserAlreadyExistsError,
)
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password


def _token_pair() -> TokenPair:
    return TokenPair(
        access_token="access.jwt",
        refresh_token="refresh.jwt",
        refresh_jti=uuid4(),
        refresh_expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )


def test_login_success(client, login_service: MagicMock) -> None:
    login_service.login = AsyncMock(return_value=_token_pair())

    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "password123",
            "device_id": "phone-1",
            "device_name": "iPhone",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access.jwt"
    assert body["refresh_token"] == "refresh.jwt"
    assert body["token_type"] == "bearer"
    login_service.login.assert_awaited_once()


def test_login_validation_error(client) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "x", "device_id": "d1"},
    )
    assert response.status_code == 422


def test_login_invalid_credentials(client, login_service: MagicMock) -> None:
    login_service.login = AsyncMock(
        side_effect=InvalidCredentialsError("Invalid email or password")
    )
    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrong-password",
            "device_id": "phone-1",
        },
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_initiate_register_success(
    client,
    initiate_register_service: MagicMock,
) -> None:
    initiate_register_service.initiate = AsyncMock(
        return_value=InitiateRegisterResult(
            detail="If this email can be used to register, a verification link has been sent.",
            registration_token="reg-token",
        )
    )
    response = client.post(
        "/auth/initiate-register",
        json={
            "email": "new@example.com",
            "password": "password123",
            "display_name": "Alice",
        },
    )
    assert response.status_code == 200
    assert "detail" in response.json()


def test_initiate_register_conflict(
    client,
    initiate_register_service: MagicMock,
) -> None:
    initiate_register_service.initiate = AsyncMock(
        side_effect=UserAlreadyExistsError("User with email new@example.com already exists")
    )
    response = client.post(
        "/auth/initiate-register",
        json={
            "email": "new@example.com",
            "password": "password123",
            "display_name": "Alice",
        },
    )
    assert response.status_code == 409


def test_complete_register_success(
    client,
    complete_register_service: MagicMock,
) -> None:
    user = User.create(
        Email("new@example.com"),
        DisplayName("Alice"),
        Password("hashed"),
    )
    complete_register_service.complete = AsyncMock(return_value=user)

    response = client.post(
        "/auth/complete-register",
        json={"token": "registration-token"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["display_name"] == "Alice"
    assert body["user_id"] == str(user.id)


def test_refresh_success(client, refresh_token_service: MagicMock) -> None:
    refresh_token_service.refresh = AsyncMock(return_value=_token_pair())
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "refresh.jwt"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == "access.jwt"


def test_logout_success(client, logout_service: MagicMock) -> None:
    logout_service.logout = AsyncMock(return_value=None)
    response = client.post(
        "/auth/logout",
        json={"refresh_token": "refresh.jwt"},
    )
    assert response.status_code == 204
    logout_service.logout.assert_awaited_once()


def test_change_password_requires_auth_override(
    client,
    change_password_service: MagicMock,
    current_user_id,
) -> None:
    change_password_service.change_password = AsyncMock(return_value=None)
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "oldpassword",
            "new_password": "newpassword1",
        },
        headers={"Authorization": "Bearer ignored-because-overridden"},
    )
    assert response.status_code == 204
    change_password_service.change_password.assert_awaited_once()
    command = change_password_service.change_password.await_args.args[0]
    assert command.user_id == current_user_id


def test_list_devices(client, list_devices_service: MagicMock, current_user_id) -> None:
    device = Device.create(
        user_id=current_user_id,
        client_device_id="phone-1",
        name="iPhone",
    )
    list_devices_service.list_devices = AsyncMock(return_value=[device])

    response = client.get(
        "/auth/devices",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["client_device_id"] == "phone-1"


def test_list_sessions(client, list_sessions_service: MagicMock, current_user_id) -> None:
    session = Session.create(
        user_id=current_user_id,
        device_id=uuid4(),
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        ip_address="127.0.0.1",
    )
    list_sessions_service.list_sessions = AsyncMock(return_value=[session])

    response = client.get(
        "/auth/sessions",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    assert response.json()[0]["id"] == str(session.id)


def test_revoke_session(client, revoke_session_service: MagicMock) -> None:
    revoke_session_service.revoke_session = AsyncMock(return_value=None)
    session_id = uuid4()
    response = client.delete(
        f"/auth/sessions/{session_id}",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 204


def test_revoke_session_not_found(
    client,
    revoke_session_service: MagicMock,
) -> None:
    revoke_session_service.revoke_session = AsyncMock(
        side_effect=SessionNotFoundError("Session not found")
    )
    response = client.delete(
        f"/auth/sessions/{uuid4()}",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 404


def test_protected_route_missing_bearer_returns_401(monkeypatch) -> None:
    """Missing Authorization hits real get_current_user_id (no DB/JWT load)."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.auth.exceptions.handlers import register_exception_handlers
    from app.auth.presentation.http import dependencies as deps
    from app.auth.presentation.http import rate_limit as rate_limit_mod
    from app.auth.presentation.http.routes import router

    async def _allow(*_a, **_k):
        return True, 0

    monkeypatch.setattr(rate_limit_mod, "get_redis", lambda: object())
    monkeypatch.setattr(rate_limit_mod.RedisRateLimiter, "check", _allow)

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_list_devices_service] = lambda: MagicMock(
        list_devices=AsyncMock(return_value=[])
    )
    app.dependency_overrides[deps.get_session_repository] = lambda: MagicMock()
    app.dependency_overrides[deps.get_token_issuer] = lambda: MagicMock()

    with TestClient(app) as test_client:
        response = test_client.get("/auth/devices")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
