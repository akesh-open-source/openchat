from __future__ import annotations

from httpx import AsyncClient

from app.gateway.infrastructure.http.client import get_http_client


def get_upstream_client() -> AsyncClient:
    return get_http_client()
