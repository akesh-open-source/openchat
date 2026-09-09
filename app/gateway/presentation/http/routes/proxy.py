from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from httpx import AsyncClient, RequestError

from app.gateway.config.settings import settings
from app.gateway.exceptions.errors import UpstreamUnavailableError
from app.gateway.presentation.http.dependencies import get_upstream_client

logger = logging.getLogger(__name__)

# Auth routes that must stay public (no edge Bearer requirement).
# Gateway currently proxies all /auth/* without JWT checks; keep this list
# as the source of truth when protecting future non-public auth paths.
PUBLIC_AUTH_PATHS = frozenset(
    {
        "initiate-register",
        "complete-register",
        "login",
        "forgot-password",
        "reset-password",
    }
)

# Hop-by-hop headers must not be forwarded (RFC 7230).
_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
        "content-length",
    }
)

router = APIRouter(tags=["proxy"])


def _filter_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in headers.items() if k.lower() not in _HOP_BY_HOP}


@router.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def proxy_auth(
    path: str,
    request: Request,
    client: Annotated[AsyncClient, Depends(get_upstream_client)],
) -> Response:
    upstream_url = f"{settings.auth_service_url.rstrip('/')}/auth/{path}"
    body = await request.body()
    headers = _filter_headers(dict(request.headers))

    try:
        upstream = await client.request(
            method=request.method,
            url=upstream_url,
            content=body,
            headers=headers,
            params=request.query_params,
        )
    except RequestError as exc:
        logger.warning("Auth upstream request failed path=%s error=%s", path, exc)
        raise UpstreamUnavailableError("auth") from exc

    # Forward upstream status/body as-is (incl. auth domain 400/401/409).
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=_filter_headers(dict(upstream.headers)),
        media_type=upstream.headers.get("content-type"),
    )
