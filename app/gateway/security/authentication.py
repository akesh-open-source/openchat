from __future__ import annotations

from uuid import UUID

import jwt
from fastapi import Request

from app.gateway.config.settings import settings
from app.gateway.exceptions.errors import InvalidTokenError, UnauthenticatedError


def extract_bearer_token(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise UnauthenticatedError("Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise UnauthenticatedError("Authorization header must be Bearer <token>")

    return token.strip()


def verify_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError("Invalid or expired access token") from exc

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid or expired access token")

    subject = payload.get("sub")
    if not subject:
        raise InvalidTokenError("Invalid or expired access token")

    try:
        return UUID(subject)
    except ValueError as exc:
        raise InvalidTokenError("Invalid or expired access token") from exc