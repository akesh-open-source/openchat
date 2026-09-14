from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.users.domain.entities.profile import Profile
from app.users.domain.value_objects.display_name import DisplayName
from app.users.exceptions.handlers import register_exception_handlers
from app.users.presentation.http import dependencies as deps
from app.users.presentation.http.routes import router


class InMemoryProfileRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Profile] = {}

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        return self._items.get(user_id)

    async def save(self, profile: Profile) -> None:
        self._items[profile.user_id] = profile

    async def delete(self, user_id: UUID) -> None:
        self._items.pop(user_id, None)


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def other_user_id() -> UUID:
    return uuid4()


@pytest.fixture
def profile_repository(user_id: UUID, other_user_id: UUID) -> InMemoryProfileRepository:
    repo = InMemoryProfileRepository()
    repo._items[user_id] = Profile.create(
        user_id=user_id,
        display_name=DisplayName("Alice"),
        email="alice@example.com",
        bio="hello",
    )
    repo._items[other_user_id] = Profile.create(
        user_id=other_user_id,
        display_name=DisplayName("Bob"),
        email="bob@example.com",
    )
    return repo


@pytest.fixture
def client(
    profile_repository: InMemoryProfileRepository,
    user_id: UUID,
) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_profile_repository] = lambda: profile_repository
    app.dependency_overrides[deps.get_current_user_id] = lambda: user_id

    with TestClient(app) as test_client:
        yield test_client


def test_get_me(client: TestClient, user_id: UUID) -> None:
    response = client.get("/users/me")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == str(user_id)
    assert body["display_name"] == "Alice"
    assert body["email"] == "alice@example.com"


def test_get_by_user_id(client: TestClient, other_user_id: UUID) -> None:
    response = client.get(f"/users/{other_user_id}")
    assert response.status_code == 200
    assert response.json()["display_name"] == "Bob"


def test_get_profile_not_found(client: TestClient) -> None:
    response = client.get(f"/users/{uuid4()}")
    assert response.status_code == 404


def test_patch_me_updates_display_name(client: TestClient, user_id: UUID) -> None:
    response = client.patch("/users/me", json={"display_name": "Alice Updated"})
    assert response.status_code == 200
    assert response.json()["display_name"] == "Alice Updated"
    assert response.json()["bio"] == "hello"


def test_patch_me_can_clear_bio(client: TestClient) -> None:
    response = client.patch("/users/me", json={"bio": ""})
    assert response.status_code == 200
    assert response.json()["bio"] is None


def test_patch_me_validation_error(client: TestClient) -> None:
    response = client.patch("/users/me", json={"display_name": "ab"})
    assert response.status_code == 422


def test_protected_route_requires_auth_when_not_overridden() -> None:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[deps.get_profile_repository] = (
        lambda: InMemoryProfileRepository()
    )

    with TestClient(app) as test_client:
        response = test_client.get("/users/me")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
