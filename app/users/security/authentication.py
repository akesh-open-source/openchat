from __future__ import annotations

from uuid import UUID

import jwt
from fastapi import Request

from app.users.config.settings import settings
from app.users.domain.exceptions import InvalidTokenError
from app.users.infrastructure.security.pem import load_pem

_public_key: str | None = None


def _get_public_key() -> str:
    global _public_key
    if _public_key is None:
        _public_key = load_pem(
            inline=settings.jwt_public_key,
            path=settings.jwt_public_key_path,
            name="public key",
        )
    return _public_key


def extract_bearer_token(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise InvalidTokenError("Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise InvalidTokenError("Authorization header must be Bearer <token>")

    return token.strip()


def verify_access_token(token: str) -> UUID:
    """Crypto-verify access JWT (public key). Session DB is owned by auth."""
    try:
        payload = jwt.decode(
            token,
            _get_public_key(),
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError("Invalid or expired access token") from exc

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid or expired access token")

    if not payload.get("sid"):
        raise InvalidTokenError("Invalid or expired access token")

    subject = payload.get("sub")
    if not subject:
        raise InvalidTokenError("Invalid or expired access token")

    try:
        UUID(str(payload["sid"]))
        return UUID(str(subject))
    except ValueError as exc:
        raise InvalidTokenError("Invalid or expired access token") from exc
