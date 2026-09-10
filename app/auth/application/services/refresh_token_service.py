from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.auth.application.commands.refresh_tokens import RefreshTokensCommand
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
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

    async def refresh(self, command: RefreshTokensCommand) -> TokenPair:
        claims = self.token_issuer.verify_refresh_token(command.refresh_token)
        now = datetime.now(timezone.utc)

        stored = await self.refresh_token_repository.get_by_id(claims.jti)
        if stored is None:
            raise InvalidTokenError("Invalid or expired refresh token")

        if stored.is_revoked:
            # Possible token theft: invalidate the whole rotation family.
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
        )
        stored.revoke(replaced_by_id=tokens.refresh_jti)

        await self.refresh_token_repository.save(replacement)
        await self.refresh_token_repository.save(stored)
        return tokens
