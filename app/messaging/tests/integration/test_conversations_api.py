from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.messaging.exceptions.handlers import register_exception_handlers
from app.messaging.presentation.http import dependencies as deps
from app.messaging.presentation.http.routes import router
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
)


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def peer_user_id() -> UUID:
    return uuid4()


@pytest.fixture
def membership_repository() -> InMemoryMembershipRepository:
    return InMemoryMembershipRepository()


@pytest.fixture
def conversation_repository(
    membership_repository: InMemoryMembershipRepository,
) -> InMemoryConversationRepository:
    return InMemoryConversationRepository(membership_repository)


@pytest.fixture
def users_client() -> MagicMock:
    client = MagicMock()
    client.user_exists = AsyncMock(return_value=True)
    return client


@pytest.fixture
def client(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
    users_client: MagicMock,
    user_id: UUID,
) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_conversation_repository] = (
        lambda: conversation_repository
    )
    app.dependency_overrides[deps.get_membership_repository] = (
        lambda: membership_repository
    )
    app.dependency_overrides[deps.get_users_client] = lambda: users_client
    app.dependency_overrides[deps.get_current_user_id] = lambda: user_id
    app.dependency_overrides[deps.get_access_token] = lambda: "test-token"

    with TestClient(app) as test_client:
        yield test_client


def test_create_then_get_same_direct_conversation_id(
    client: TestClient,
    peer_user_id: UUID,
    users_client: MagicMock,
) -> None:
    first = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    assert first.status_code == 200
    body = first.json()
    assert body["type"] == "direct"
    assert body["peer_user_id"] == str(peer_user_id)
    assert body["created"] is True
    conversation_id = body["id"]

    second = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    assert second.status_code == 200
    assert second.json()["id"] == conversation_id
    assert second.json()["created"] is False
    assert users_client.user_exists.await_count >= 2


def test_create_direct_rejects_unknown_peer(
    client: TestClient,
    peer_user_id: UUID,
    users_client: MagicMock,
) -> None:
    users_client.user_exists = AsyncMock(return_value=False)
    response = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    assert response.status_code == 404


def test_create_direct_rejects_self_chat(
    client: TestClient,
    user_id: UUID,
) -> None:
    response = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(user_id)},
    )
    assert response.status_code == 400


def test_create_direct_requires_auth(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
    users_client: MagicMock,
    peer_user_id: UUID,
) -> None:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_conversation_repository] = (
        lambda: conversation_repository
    )
    app.dependency_overrides[deps.get_membership_repository] = (
        lambda: membership_repository
    )
    app.dependency_overrides[deps.get_users_client] = lambda: users_client
    # Do not override auth deps — missing Bearer → 401.

    with TestClient(app) as test_client:
        response = test_client.post(
            "/conversations/direct",
            json={"peer_user_id": str(peer_user_id)},
        )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_list_conversations_returns_only_caller_memberships(
    client: TestClient,
    peer_user_id: UUID,
) -> None:
    created = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    assert created.status_code == 200
    conversation_id = created.json()["id"]

    listed = client.get("/conversations")
    assert listed.status_code == 200
    body = listed.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == conversation_id
    assert body["items"][0]["peer_user_id"] == str(peer_user_id)
    assert body["items"][0]["peer_display_name"] is None
    assert body["next_cursor"] is None


def test_get_conversation_by_id_for_member(
    client: TestClient,
    peer_user_id: UUID,
) -> None:
    created = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    conversation_id = created.json()["id"]

    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json()["id"] == conversation_id
    assert response.json()["peer_user_id"] == str(peer_user_id)


def test_get_conversation_by_id_for_non_member_returns_404(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
    users_client: MagicMock,
    user_id: UUID,
    peer_user_id: UUID,
) -> None:
    # Create as user_id, then fetch as a stranger.
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_conversation_repository] = (
        lambda: conversation_repository
    )
    app.dependency_overrides[deps.get_membership_repository] = (
        lambda: membership_repository
    )
    app.dependency_overrides[deps.get_users_client] = lambda: users_client
    app.dependency_overrides[deps.get_current_user_id] = lambda: user_id
    app.dependency_overrides[deps.get_access_token] = lambda: "test-token"

    with TestClient(app) as owner_client:
        created = owner_client.post(
            "/conversations/direct",
            json={"peer_user_id": str(peer_user_id)},
        )
        assert created.status_code == 200
        conversation_id = created.json()["id"]

    stranger_id = uuid4()
    app.dependency_overrides[deps.get_current_user_id] = lambda: stranger_id
    with TestClient(app) as stranger_client:
        response = stranger_client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 404


def test_list_conversations_cursor_pagination(
    client: TestClient,
) -> None:
    ids: list[str] = []
    for _ in range(3):
        response = client.post(
            "/conversations/direct",
            json={"peer_user_id": str(uuid4())},
        )
        assert response.status_code == 200
        ids.append(response.json()["id"])

    first = client.get("/conversations", params={"limit": 2})
    assert first.status_code == 200
    assert len(first.json()["items"]) == 2
    assert first.json()["next_cursor"] is not None

    second = client.get(
        "/conversations",
        params={"limit": 2, "cursor": first.json()["next_cursor"]},
    )
    assert second.status_code == 200
    assert len(second.json()["items"]) == 1
    assert second.json()["next_cursor"] is None

    seen = {item["id"] for item in first.json()["items"]} | {
        item["id"] for item in second.json()["items"]
    }
    assert seen == set(ids)
