from __future__ import annotations

from dataclasses import dataclass

from app.auth.application.commands.login_user import LoginUserCommand
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.token_issuer import TokenIssuer, TokenPair
from app.auth.domain.entities.refresh_token import RefreshToken, new_refresh_family_id
from app.auth.domain.exceptions import InvalidCredentialsError
from app.auth.domain.value_objects.email import Email
from app.auth.infrastructure.security.token_hash import hash_token


@dataclass(slots=True)
class LoginService:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_issuer: TokenIssuer
    refresh_token_repository: RefreshTokenRepository

    async def login(self, command: LoginUserCommand) -> TokenPair:
        email = Email(command.email)

        user = await self.user_repository.get_by_email(email.value)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password")

        if not self.password_hasher.verify(
            command.password,
            user.password.hashed_value,
        ):
            raise InvalidCredentialsError("Invalid email or password")

        tokens = self.token_issuer.issue_tokens(user.id, user.email.value)
        await self.refresh_token_repository.save(
            RefreshToken.create(
                token_id=tokens.refresh_jti,
                user_id=user.id,
                token_hash=hash_token(tokens.refresh_token),
                family_id=new_refresh_family_id(),
                expires_at=tokens.refresh_expires_at,
            )
        )
        return tokens
