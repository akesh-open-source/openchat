from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.users.exceptions.handlers import register_exception_handlers
from app.users.presentation.http.routes import router


def test_health_smoke() -> None:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
