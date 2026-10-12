from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi import Request

from app.gateway.exceptions.errors import InvalidTokenError, UnauthenticatedError
from app.gateway.security import authentication as auth_mod


@pytest.fixture(autouse=True)
def _reset_public_key_cache() -> None:
    auth_mod._public_key = None
    yield
    auth_mod._public_key = None


@pytest.fixture
def public_key(rsa_pem_pair, monkeypatch) -> str:
    monkeypatch.setattr(auth_mod, "_public_key", rsa_pem_pair.public_pem)
    monkeypatch.setattr(auth_mod.settings, "jwt_algorithm", "RS256")
    return rsa_pem_pair.public_pem


def _access_token(private_pem: str, *, sid: str | None = None, typ: str = "access") -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": str(uuid4()),
        "email": "user@example.com",
        "type": typ,
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }
    if sid is not None:
        payload["sid"] = sid
    return jwt.encode(payload, private_pem, algorithm="RS256")


def test_verify_access_token_success(rsa_pem_pair, public_key: str) -> None:
    session_id = uuid4()
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "email": "user@example.com",
            "type": "access",
            "sid": str(session_id),
            "iat": now,
            "exp": now + timedelta(minutes=15),
        },
        rsa_pem_pair.private_pem,
        algorithm="RS256",
    )
    assert auth_mod.verify_access_token(token) == user_id


def test_verify_access_token_requires_sid(rsa_pem_pair, public_key: str) -> None:
    token = _access_token(rsa_pem_pair.private_pem, sid=None)
    with pytest.raises(InvalidTokenError):
        auth_mod.verify_access_token(token)


def test_verify_access_token_rejects_refresh(rsa_pem_pair, public_key: str) -> None:
    token = _access_token(
        rsa_pem_pair.private_pem,
        sid=str(uuid4()),
        typ="refresh",
    )
    with pytest.raises(InvalidTokenError):
        auth_mod.verify_access_token(token)


def test_verify_access_token_rejects_bad_signature(rsa_pem_pair, public_key: str) -> None:
    token = _access_token(rsa_pem_pair.private_pem, sid=str(uuid4()))
    with pytest.raises(InvalidTokenError):
        auth_mod.verify_access_token(token + "tampered")


def test_extract_bearer_token_success() -> None:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"authorization", b"Bearer tok.en")],
        }
    )
    assert auth_mod.extract_bearer_token(request) == "tok.en"


def test_extract_bearer_token_missing() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    with pytest.raises(UnauthenticatedError):
        auth_mod.extract_bearer_token(request)
