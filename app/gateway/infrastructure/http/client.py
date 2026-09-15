from __future__ import annotations

from httpx import AsyncClient

from app.gateway.config.settings import settings

_http_client: AsyncClient | None = None


async def init_http_client() -> AsyncClient:
    global _http_client
    _http_client = AsyncClient(timeout=settings.http_timeout_seconds)
    return _http_client


async def close_http_client() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


def get_http_client() -> AsyncClient:
    if _http_client is None:
        raise RuntimeError("HTTP client is not initialized")
    return _http_client
