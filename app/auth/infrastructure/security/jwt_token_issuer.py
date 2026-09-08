from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.auth.application.ports.token_issuer import TokenPair
from app.auth.domain.exceptions import InvalidTokenError


class JwtTokenIssuer:
    def __init__(
        self,
        *,
        secret: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._access_ttl = timedelta(minutes=access_token_expire_minutes)
        self._refresh_ttl = timedelta(days=refresh_token_expire_days)

    def issue_tokens(self, user_id: UUID, email: str) -> TokenPair:
        now = datetime.now(timezone.utc)
        subject = str(user_id)

        access_token = jwt.encode(
            {
                "sub": subject,
                "email": email,
                "type": "access",
                "iat": now,
                "exp": now + self._access_ttl,
            },
            self._secret,
            algorithm=self._algorithm,
        )
        refresh_token = jwt.encode(
            {
                "sub": subject,
                "email": email,
                "type": "refresh",
                "iat": now,
                "exp": now + self._refresh_ttl,
            },
            self._secret,
            algorithm=self._algorithm,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def verify_access_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
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
