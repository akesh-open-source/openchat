from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from httpx import AsyncClient

from app.gateway.infrastructure.http.client import get_http_client
from app.gateway.security.authentication import (
    extract_bearer_token,
    verify_access_token,
)


def get_upstream_client() -> AsyncClient:
    return get_http_client()


def get_current_user_id(request: Request) -> UUID:
    """Require a valid Bearer access token issued by auth (edge JWT check)."""
    token = extract_bearer_token(request)
    return verify_access_token(token)


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
