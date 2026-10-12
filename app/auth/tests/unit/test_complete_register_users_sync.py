from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import httpx

from app.auth.application.commands.complete_register import CompleteRegisterCommand
from app.auth.application.ports.pending_registration_store import PendingRegistration
from app.auth.application.services.complete_register_service import (
    CompleteRegisterService,
)
from app.auth.infrastructure.http.users_client import HttpxUsersClient


def _pending() -> PendingRegistration:
    return PendingRegistration(
        email="alice@example.com",
        password_hash="hashed-password",
        display_name="Alice",
    )


def _service(*, users_client: MagicMock) -> CompleteRegisterService:
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


def test_complete_register_calls_users_client() -> None:
    async def _run() -> None:
        users_client = MagicMock()
        users_client.create_profile = AsyncMock()
        service = _service(users_client=users_client)

        user = await service.complete(CompleteRegisterCommand(token="tok"))

        users_client.create_profile.assert_awaited_once()
        kwargs = users_client.create_profile.await_args.kwargs
        assert kwargs["user_id"] == user.id
        assert kwargs["display_name"] == "Alice"
        assert kwargs["email"] == "alice@example.com"

    asyncio.run(_run())


def test_complete_register_continues_when_users_client_fails() -> None:
    async def _run() -> None:
        users_client = MagicMock()
        users_client.create_profile = AsyncMock(side_effect=httpx.ConnectError("down"))
        service = _service(users_client=users_client)

        user = await service.complete(CompleteRegisterCommand(token="tok"))
        assert user.email.value == "alice@example.com"
        service.user_repository.save.assert_awaited_once()

    asyncio.run(_run())


def test_httpx_users_client_posts_internal_profiles() -> None:
    async def _run() -> None:
        user_id = uuid4()
        captured: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"created": True})

        transport = httpx.MockTransport(handler)
        real_async_client = httpx.AsyncClient

        def async_client_factory(*args: object, **kwargs: object) -> httpx.AsyncClient:
            kwargs = dict(kwargs)
            kwargs["transport"] = transport
            return real_async_client(*args, **kwargs)

        client = HttpxUsersClient(base_url="http://users.test", timeout_seconds=2.0)
        with patch(
            "app.auth.infrastructure.http.users_client.httpx.AsyncClient",
            side_effect=async_client_factory,
        ):
            await client.create_profile(
                user_id=user_id,
                display_name="Alice",
                email="alice@example.com",
            )

        assert captured["url"] == "http://users.test/internal/profiles"
        assert captured["body"] == {
            "user_id": str(user_id),
            "display_name": "Alice",
            "email": "alice@example.com",
        }

    asyncio.run(_run())
