from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.auth.application.ports.token_issuer import TokenPair
from app.auth.domain.exceptions import InvalidTokenError

_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"
_PASSWORD_RESET_TYPE = "password_reset"


class JwtTokenIssuer:
    def __init__(
        self,
        *,
        secret: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
        password_reset_token_expire_minutes: int,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._access_ttl = timedelta(minutes=access_token_expire_minutes)
        self._refresh_ttl = timedelta(days=refresh_token_expire_days)
        self._password_reset_ttl = timedelta(
            minutes=password_reset_token_expire_minutes,
        )

    def issue_tokens(self, user_id: UUID, email: str) -> TokenPair:
        now = datetime.now(timezone.utc)
        subject = str(user_id)

        access_token = self._encode(
            subject=subject,
            email=email,
            token_type=_ACCESS_TYPE,
            expires_at=now + self._access_ttl,
            now=now,
        )
        refresh_token = self._encode(
            subject=subject,
            email=email,
            token_type=_REFRESH_TYPE,
            expires_at=now + self._refresh_ttl,
            now=now,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def verify_access_token(self, token: str) -> UUID:
        return self._verify(token, expected_type=_ACCESS_TYPE)

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
        return self._verify(token, expected_type=_PASSWORD_RESET_TYPE)

    def _encode(
        self,
        *,
        subject: str,
        email: str,
        token_type: str,
        expires_at: datetime,
        now: datetime,
    ) -> str:
        return jwt.encode(
            {
                "sub": subject,
                "email": email,
                "type": token_type,
                "iat": now,
                "exp": expires_at,
            },
            self._secret,
            algorithm=self._algorithm,
        )

    def _verify(self, token: str, *, expected_type: str) -> UUID:
        error_message = (
            "Invalid or expired reset token"
            if expected_type == _PASSWORD_RESET_TYPE
            else "Invalid or expired access token"
        )
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError(error_message) from exc

        if payload.get("type") != expected_type:
            raise InvalidTokenError(error_message)

        subject = payload.get("sub")
        if not subject:
            raise InvalidTokenError(error_message)

        try:
            return UUID(subject)
        except ValueError as exc:
            raise InvalidTokenError(error_message) from exc
