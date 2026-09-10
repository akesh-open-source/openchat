from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from app.auth.domain.exceptions import InvalidTokenError
from app.auth.infrastructure.security.jwt_token_issuer import JwtTokenIssuer


@pytest.fixture
def issuer(rsa_pem_pair) -> JwtTokenIssuer:
    return JwtTokenIssuer(
        private_key=rsa_pem_pair.private_pem,
        public_key=rsa_pem_pair.public_pem,
        algorithm="RS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
        password_reset_token_expire_minutes=30,
    )


def test_issue_and_verify_access_token(issuer: JwtTokenIssuer) -> None:
    user_id = uuid4()
    session_id = uuid4()
    pair = issuer.issue_tokens(user_id, "user@example.com", session_id=session_id)

    claims = issuer.verify_access_token(pair.access_token)
    assert claims.user_id == user_id
    assert claims.session_id == session_id


def test_issue_and_verify_refresh_token(issuer: JwtTokenIssuer) -> None:
    user_id = uuid4()
    pair = issuer.issue_tokens(user_id, "user@example.com", session_id=uuid4())

    claims = issuer.verify_refresh_token(pair.refresh_token)
    assert claims.user_id == user_id
    assert claims.email == "user@example.com"
    assert claims.jti == pair.refresh_jti


def test_access_token_rejects_missing_sid(
    issuer: JwtTokenIssuer,
    rsa_pem_pair,
) -> None:
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "email": "user@example.com",
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=15),
        },
        rsa_pem_pair.private_pem,
        algorithm="RS256",
    )
    with pytest.raises(InvalidTokenError):
        issuer.verify_access_token(token)


def test_verify_rejects_wrong_token_type(issuer: JwtTokenIssuer) -> None:
    pair = issuer.issue_tokens(uuid4(), "user@example.com", session_id=uuid4())
    with pytest.raises(InvalidTokenError, match="access token"):
        issuer.verify_access_token(pair.refresh_token)
    with pytest.raises(InvalidTokenError, match="refresh token"):
        issuer.verify_refresh_token(pair.access_token)


def test_password_reset_token_roundtrip(issuer: JwtTokenIssuer) -> None:
    user_id = uuid4()
    token = issuer.issue_password_reset_token(user_id, "user@example.com")
    assert issuer.verify_password_reset_token(token) == user_id


def test_verify_rejects_tampered_token(issuer: JwtTokenIssuer) -> None:
    pair = issuer.issue_tokens(uuid4(), "user@example.com", session_id=uuid4())
    with pytest.raises(InvalidTokenError):
        issuer.verify_access_token(pair.access_token + "x")


def test_refresh_token_ttl(issuer: JwtTokenIssuer) -> None:
    assert issuer.refresh_token_ttl == timedelta(days=7)
