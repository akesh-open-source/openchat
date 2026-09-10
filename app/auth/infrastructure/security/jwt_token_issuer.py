from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.auth.application.ports.token_issuer import (
    AccessTokenClaims,
    RefreshTokenClaims,
    TokenPair,
)
from app.auth.domain.exceptions import InvalidTokenError
from app.auth.domain.ids import new_uuid7

_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"
_PASSWORD_RESET_TYPE = "password_reset"


class JwtTokenIssuer:
    """Issues and verifies JWTs using asymmetric keys (sign=private, verify=public)."""

    def __init__(
        self,
        *,
        private_key: str,
        public_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
        password_reset_token_expire_minutes: int,
    ) -> None:
        self._private_key = private_key
        self._public_key = public_key
        self._algorithm = algorithm
        self._access_ttl = timedelta(minutes=access_token_expire_minutes)
        self._refresh_ttl = timedelta(days=refresh_token_expire_days)
        self._password_reset_ttl = timedelta(
            minutes=password_reset_token_expire_minutes,
        )

    def issue_tokens(
        self,
        user_id: UUID,
        email: str,
        *,
        session_id: UUID,
    ) -> TokenPair:
        now = datetime.now(timezone.utc)
        subject = str(user_id)
        refresh_jti = new_uuid7()
        refresh_expires_at = now + self._refresh_ttl

        access_token = self._encode(
            subject=subject,
            email=email,
            token_type=_ACCESS_TYPE,
            expires_at=now + self._access_ttl,
            now=now,
            session_id=session_id,
        )
        refresh_token = self._encode(
            subject=subject,
            email=email,
            token_type=_REFRESH_TYPE,
            expires_at=refresh_expires_at,
            now=now,
            jti=refresh_jti,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            refresh_jti=refresh_jti,
            refresh_expires_at=refresh_expires_at,
        )

    def verify_access_token(self, token: str) -> AccessTokenClaims:
        payload = self._decode(token, expected_type=_ACCESS_TYPE)
        user_id = self._subject_uuid(payload, expected_type=_ACCESS_TYPE)
        session_raw = payload.get("sid")
        if not session_raw:
            raise InvalidTokenError("Invalid or expired access token")
        try:
            session_id = UUID(str(session_raw))
        except ValueError as exc:
            raise InvalidTokenError("Invalid or expired access token") from exc
        return AccessTokenClaims(user_id=user_id, session_id=session_id)

    def verify_refresh_token(self, token: str) -> RefreshTokenClaims:
        payload = self._decode(token, expected_type=_REFRESH_TYPE)
        user_id = self._subject_uuid(payload, expected_type=_REFRESH_TYPE)
        email = payload.get("email")
        jti_raw = payload.get("jti")
        if not email or not jti_raw:
            raise InvalidTokenError("Invalid or expired refresh token")
        try:
            jti = UUID(str(jti_raw))
        except ValueError as exc:
            raise InvalidTokenError("Invalid or expired refresh token") from exc
        return RefreshTokenClaims(user_id=user_id, email=str(email), jti=jti)

    def issue_password_reset_token(self, user_id: UUID, email: str) -> str:
        now = datetime.now(timezone.utc)
        return self._encode(
            subject=str(user_id),
            email=email,
            token_type=_PASSWORD_RESET_TYPE,
            expires_at=now + self._password_reset_ttl,
            now=now,
        )

    def verify_password_reset_token(self, token: str) -> UUID:
        payload = self._decode(token, expected_type=_PASSWORD_RESET_TYPE)
        return self._subject_uuid(payload, expected_type=_PASSWORD_RESET_TYPE)

    @property
    def refresh_token_ttl(self) -> timedelta:
        return self._refresh_ttl

    def _encode(
        self,
        *,
        subject: str,
        email: str,
        token_type: str,
        expires_at: datetime,
        now: datetime,
        jti: UUID | None = None,
        session_id: UUID | None = None,
    ) -> str:
        payload: dict[str, object] = {
            "sub": subject,
            "email": email,
            "type": token_type,
            "iat": now,
            "exp": expires_at,
        }
        if jti is not None:
            payload["jti"] = str(jti)
        if session_id is not None:
            payload["sid"] = str(session_id)
        return jwt.encode(
            payload,
            self._private_key,
            algorithm=self._algorithm,
        )

    def _decode(self, token: str, *, expected_type: str) -> dict:
        error_message = self._error_message(expected_type)
        try:
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=[self._algorithm],
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError(error_message) from exc

        if payload.get("type") != expected_type:
            raise InvalidTokenError(error_message)
        return payload

    def _subject_uuid(self, payload: dict, *, expected_type: str) -> UUID:
        error_message = self._error_message(expected_type)
        subject = payload.get("sub")
        if not subject:
            raise InvalidTokenError(error_message)
        try:
            return UUID(str(subject))
        except ValueError as exc:
            raise InvalidTokenError(error_message) from exc

    @staticmethod
    def _error_message(expected_type: str) -> str:
        if expected_type == _PASSWORD_RESET_TYPE:
            return "Invalid or expired reset token"
        if expected_type == _REFRESH_TYPE:
            return "Invalid or expired refresh token"
        return "Invalid or expired access token"
