from __future__ import annotations

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
def conversation_repository() -> InMemoryConversationRepository:
    return InMemoryConversationRepository()


@pytest.fixture
def membership_repository() -> InMemoryMembershipRepository:
    return InMemoryMembershipRepository()


@pytest.fixture
def client(
    conversation_repository: InMemoryConversationRepository,
    membership_repository: InMemoryMembershipRepository,
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
    app.dependency_overrides[deps.get_current_user_id] = lambda: user_id

    with TestClient(app) as test_client:
        yield test_client


def test_create_then_get_same_direct_conversation_id(
    client: TestClient,
    peer_user_id: UUID,
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
    # Do not override get_current_user_id — missing Bearer → 401.

    with TestClient(app) as test_client:
        response = test_client.post(
            "/conversations/direct",
            json={"peer_user_id": str(peer_user_id)},
        )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
