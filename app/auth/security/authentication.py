from __future__ import annotations

from fastapi import Request

from app.auth.domain.exceptions import InvalidTokenError


def extract_bearer_token(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise InvalidTokenError("Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise InvalidTokenError("Authorization header must be Bearer <token>")

    return token.strip()
