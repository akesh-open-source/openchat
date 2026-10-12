from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.messaging.domain.entities.message import Message
from app.messaging.exceptions.handlers import register_exception_handlers
from app.messaging.presentation.http import dependencies as deps
from app.messaging.presentation.http.routes import router
from app.messaging.tests.unit.test_repositories import (
    InMemoryConversationRepository,
    InMemoryMembershipRepository,
    InMemoryMessageRepository,
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
def message_repository(
    conversation_repository: InMemoryConversationRepository,
) -> InMemoryMessageRepository:
    return InMemoryMessageRepository(conversation_repository)


@pytest.fixture
def users_client() -> MagicMock:
    client = MagicMock()
    client.user_exists = AsyncMock(return_value=True)
    client.get_display_names = AsyncMock(
        side_effect=lambda *, user_ids, access_token: {
            uid: f"User-{str(uid)[:8]}" for uid in user_ids
        },
    )
    return client


@pytest.fixture
def client(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
    message_repository: InMemoryMessageRepository,
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
    app.dependency_overrides[deps.get_message_repository] = lambda: message_repository
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
    message_repository: InMemoryMessageRepository,
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
    app.dependency_overrides[deps.get_message_repository] = lambda: message_repository
    app.dependency_overrides[deps.get_users_client] = lambda: users_client
    # Do not override auth deps — missing Bearer → 401.

    with TestClient(app) as test_client:
        response = test_client.post(
            "/conversations/direct",
            json={"peer_user_id": str(peer_user_id)},
        )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_list_conversations_returns_peer_name_and_empty_preview(
    client: TestClient,
    peer_user_id: UUID,
    users_client: MagicMock,
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
    item = body["items"][0]
    assert item["id"] == conversation_id
    assert item["peer_user_id"] == str(peer_user_id)
    assert item["peer_display_name"] == f"User-{str(peer_user_id)[:8]}"
    assert item["last_message_preview"] is None
    assert item["last_message_at"] is None
    assert body["next_cursor"] is None
    users_client.get_display_names.assert_awaited()


def test_list_conversations_includes_last_message_preview(
    client: TestClient,
    peer_user_id: UUID,
    message_repository: InMemoryMessageRepository,
    user_id: UUID,
) -> None:
    created = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    conversation_id = UUID(created.json()["id"])
    message = Message.create(
        conversation_id=conversation_id,
        sender_id=user_id,
        client_message_id="cid-1",
        sequence=1,
        body="latest preview text",
    )
    asyncio.run(message_repository.save(message))

    listed = client.get("/conversations")
    assert listed.status_code == 200
    item = listed.json()["items"][0]
    assert item["last_message_preview"] == "latest preview text"
    assert item["last_message_at"] is not None


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
    body = response.json()
    assert body["id"] == conversation_id
    assert body["peer_user_id"] == str(peer_user_id)
    assert body["peer_display_name"] == f"User-{str(peer_user_id)[:8]}"


def test_get_conversation_by_id_for_non_member_returns_404(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
    message_repository: InMemoryMessageRepository,
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
    app.dependency_overrides[deps.get_message_repository] = lambda: message_repository
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


def test_send_message_happy_path_assigns_server_sequence(
    client: TestClient,
    peer_user_id: UUID,
) -> None:
    created = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    assert created.status_code == 200
    conversation_id = created.json()["id"]

    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"client_message_id": "phone-1", "body": "hello"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == conversation_id
    assert body["client_message_id"] == "phone-1"
    assert body["body"] == "hello"
    assert body["sequence"] == 1
    assert body["status"] == "SENT"
    assert body["created"] is True


def test_send_message_retry_same_client_message_id_returns_original(
    client: TestClient,
    peer_user_id: UUID,
) -> None:
    created = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    conversation_id = created.json()["id"]

    first = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"client_message_id": "retry-me", "body": "once"},
    )
    assert first.status_code == 200
    first_body = first.json()

    second = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"client_message_id": "retry-me", "body": "once"},
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["id"] == first_body["id"]
    assert second_body["sequence"] == first_body["sequence"]
    assert second_body["created"] is False

    third = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"client_message_id": "other", "body": "two"},
    )
    assert third.status_code == 200
    assert third.json()["sequence"] == 2


def test_send_message_outsider_gets_404(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
    message_repository: InMemoryMessageRepository,
    users_client: MagicMock,
    user_id: UUID,
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
    app.dependency_overrides[deps.get_message_repository] = lambda: message_repository
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
        response = stranger_client.post(
            f"/conversations/{conversation_id}/messages",
            json={"client_message_id": "nope", "body": "secret"},
        )
    assert response.status_code == 404


def test_list_messages_cursor_pages_contiguous_by_sequence(
    client: TestClient,
    peer_user_id: UUID,
) -> None:
    created = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    conversation_id = created.json()["id"]
    for i in range(1, 6):
        sent = client.post(
            f"/conversations/{conversation_id}/messages",
            json={"client_message_id": f"m{i}", "body": f"body-{i}"},
        )
        assert sent.status_code == 200
        assert sent.json()["sequence"] == i

    first = client.get(
        f"/conversations/{conversation_id}/messages",
        params={"limit": 2},
    )
    assert first.status_code == 200
    first_body = first.json()
    assert [item["sequence"] for item in first_body["items"]] == [1, 2]
    assert first_body["next_cursor"] is not None

    second = client.get(
        f"/conversations/{conversation_id}/messages",
        params={"limit": 2, "cursor": first_body["next_cursor"]},
    )
    assert second.status_code == 200
    second_body = second.json()
    assert [item["sequence"] for item in second_body["items"]] == [3, 4]
    assert second_body["next_cursor"] is not None

    third = client.get(
        f"/conversations/{conversation_id}/messages",
        params={"limit": 2, "cursor": second_body["next_cursor"]},
    )
    assert third.status_code == 200
    third_body = third.json()
    assert [item["sequence"] for item in third_body["items"]] == [5]
    assert third_body["next_cursor"] is None


def test_list_messages_bad_cursor_returns_400(
    client: TestClient,
    peer_user_id: UUID,
) -> None:
    created = client.post(
        "/conversations/direct",
        json={"peer_user_id": str(peer_user_id)},
    )
    conversation_id = created.json()["id"]
    response = client.get(
        f"/conversations/{conversation_id}/messages",
        params={"cursor": "%%%not-valid%%%"},
    )
    assert response.status_code == 400


def test_message_routes_unknown_conversation_id_gets_404(
    client: TestClient,
) -> None:
    missing_id = uuid4()
    listed = client.get(f"/conversations/{missing_id}/messages")
    assert listed.status_code == 404
    sent = client.post(
        f"/conversations/{missing_id}/messages",
        json={"client_message_id": "x", "body": "hi"},
    )
    assert sent.status_code == 404
    got = client.get(f"/conversations/{missing_id}")
    assert got.status_code == 404


def test_list_messages_outsider_gets_404(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
    message_repository: InMemoryMessageRepository,
    users_client: MagicMock,
    user_id: UUID,
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
    app.dependency_overrides[deps.get_message_repository] = lambda: message_repository
    app.dependency_overrides[deps.get_users_client] = lambda: users_client
    app.dependency_overrides[deps.get_current_user_id] = lambda: user_id
    app.dependency_overrides[deps.get_access_token] = lambda: "test-token"

    with TestClient(app) as owner_client:
        created = owner_client.post(
            "/conversations/direct",
            json={"peer_user_id": str(peer_user_id)},
        )
        conversation_id = created.json()["id"]
        owner_client.post(
            f"/conversations/{conversation_id}/messages",
            json={"client_message_id": "secret", "body": "hi"},
        )

    stranger_id = uuid4()
    app.dependency_overrides[deps.get_current_user_id] = lambda: stranger_id
    with TestClient(app) as stranger_client:
        response = stranger_client.get(f"/conversations/{conversation_id}/messages")
    assert response.status_code == 404
