from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.auth.application.commands.reset_password import ResetPasswordCommand
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.token_issuer import TokenIssuer
from app.auth.domain.exceptions import InvalidTokenError
from app.auth.domain.value_objects.password import Password


@dataclass(slots=True)
class ResetPasswordService:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_issuer: TokenIssuer
    refresh_token_repository: RefreshTokenRepository

    async def reset_password(self, command: ResetPasswordCommand) -> None:
        user_id = self.token_issuer.verify_password_reset_token(command.token)

        user = await self.user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError("Invalid or expired reset token")

        Password.validate_plain(command.new_password)
        hashed = self.password_hasher.hash(command.new_password)
        user.update_password(Password(hashed))
        await self.user_repository.save(user)
        await self.refresh_token_repository.revoke_all_for_user(
            user.id,
            at=datetime.now(timezone.utc),
        )
