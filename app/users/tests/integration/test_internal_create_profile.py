from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.users.domain.entities.profile import Profile
from app.users.exceptions.handlers import register_exception_handlers
from app.users.presentation.http import dependencies as deps
from app.users.presentation.http.routes import router


class InMemoryProfileRepository:
    def __init__(self) -> None:
        self._items: dict = {}

    async def get_by_user_id(self, user_id):
        return self._items.get(user_id)

    async def get_by_email(self, email: str):
        normalized = email.strip().lower()
        for profile in self._items.values():
            if profile.email == normalized:
                return profile
        return None

    async def save(self, profile: Profile) -> None:
        self._items[profile.user_id] = profile

    async def delete(self, user_id) -> None:
        self._items.pop(user_id, None)


@pytest.fixture
def profile_repository() -> InMemoryProfileRepository:
    return InMemoryProfileRepository()


@pytest.fixture
def client(profile_repository: InMemoryProfileRepository) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_profile_repository] = lambda: profile_repository

    with TestClient(app) as test_client:
        yield test_client


def test_create_profile_twice_is_idempotent(
    client: TestClient,
    profile_repository: InMemoryProfileRepository,
) -> None:
    user_id = str(uuid4())
    payload = {
        "user_id": user_id,
        "display_name": "Alice",
        "email": "alice@example.com",
    }

    first = client.post("/internal/profiles", json=payload)
    assert first.status_code == 200
    body = first.json()
    assert body["created"] is True
    assert body["user_id"] == user_id
    assert body["display_name"] == "Alice"
    assert body["email"] == "alice@example.com"
    assert len(profile_repository._items) == 1

    second = client.post("/internal/profiles", json=payload)
    assert second.status_code == 200
    assert second.json()["created"] is False
    assert second.json()["user_id"] == user_id
    assert len(profile_repository._items) == 1


def test_create_profile_validation_error(client: TestClient) -> None:
    response = client.post(
        "/internal/profiles",
        json={"user_id": "not-a-uuid", "display_name": "ab"},
    )
    assert response.status_code == 422
