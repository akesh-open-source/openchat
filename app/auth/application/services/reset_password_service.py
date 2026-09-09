from __future__ import annotations

from dataclasses import dataclass

from app.auth.application.commands.reset_password import ResetPasswordCommand
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.token_issuer import TokenIssuer
from app.auth.domain.exceptions import InvalidTokenError
from app.auth.domain.value_objects.password import Password


@dataclass(slots=True)
class ResetPasswordService:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_issuer: TokenIssuer

    async def reset_password(self, command: ResetPasswordCommand) -> None:
        user_id = self.token_issuer.verify_password_reset_token(command.token)

        user = await self.user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError("Invalid or expired reset token")

        Password.validate_plain(command.new_password)
        hashed = self.password_hasher.hash(command.new_password)
        user.update_password(Password(hashed))
        await self.user_repository.save(user)
