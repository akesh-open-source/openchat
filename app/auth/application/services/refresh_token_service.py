from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.auth.application.commands.refresh_tokens import RefreshTokensCommand
from app.auth.application.ports.repositories.device_repository import DeviceRepository
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.session_repository import SessionRepository
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.token_issuer import TokenIssuer, TokenPair
from app.auth.domain.entities.refresh_token import RefreshToken
from app.auth.domain.exceptions import InvalidTokenError
from app.auth.infrastructure.security.token_hash import hash_token


@dataclass(slots=True)
class RefreshTokenService:
    user_repository: UserRepository
    refresh_token_repository: RefreshTokenRepository
    token_issuer: TokenIssuer
    session_repository: SessionRepository
    device_repository: DeviceRepository

    async def refresh(self, command: RefreshTokensCommand) -> TokenPair:
        claims = self.token_issuer.verify_refresh_token(command.refresh_token)
        now = datetime.now(timezone.utc)

        stored = await self.refresh_token_repository.get_by_id(claims.jti)
        if stored is None:
            raise InvalidTokenError("Invalid or expired refresh token")

        if stored.is_revoked:
            await self.refresh_token_repository.revoke_family(
                stored.family_id,
                at=now,
            )
            raise InvalidTokenError("Invalid or expired refresh token")

        if stored.expires_at <= now:
            raise InvalidTokenError("Invalid or expired refresh token")

        if stored.token_hash != hash_token(command.refresh_token):
            raise InvalidTokenError("Invalid or expired refresh token")

        if stored.user_id != claims.user_id:
            raise InvalidTokenError("Invalid or expired refresh token")

        if stored.session_id is None:
            raise InvalidTokenError("Invalid or expired refresh token")

        session = await self.session_repository.get_by_id(stored.session_id)
        if session is None or not session.is_active or session.user_id != claims.user_id:
            raise InvalidTokenError("Invalid or expired refresh token")

        user = await self.user_repository.get_by_id(claims.user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError("Invalid or expired refresh token")

        tokens = self.token_issuer.issue_tokens(user.id, user.email.value)
        replacement = RefreshToken.create(
            token_id=tokens.refresh_jti,
            user_id=user.id,
            token_hash=hash_token(tokens.refresh_token),
            family_id=stored.family_id,
            expires_at=tokens.refresh_expires_at,
            session_id=session.id,
        )
        stored.revoke(replaced_by_id=tokens.refresh_jti)
        session.touch(expires_at=tokens.refresh_expires_at)

        device = await self.device_repository.get_by_id(session.device_id)
        if device is not None:
            device.touch()
            await self.device_repository.save(device)

        await self.refresh_token_repository.save(replacement)
        await self.refresh_token_repository.save(stored)
        await self.session_repository.save(session)
        return tokens
