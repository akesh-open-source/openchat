from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.auth.application.commands.change_password import ChangePasswordCommand
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.domain.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
    InvalidTokenError,
)
from app.auth.domain.value_objects.password import Password


@dataclass(slots=True)
class ChangePasswordService:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    refresh_token_repository: RefreshTokenRepository

    async def change_password(self, command: ChangePasswordCommand) -> None:
        user = await self.user_repository.get_by_id(command.user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError("Invalid or expired access token")

        if not self.password_hasher.verify(
            command.current_password,
            user.password.hashed_value,
        ):
            raise InvalidCredentialsError("Current password is incorrect")

        Password.validate_plain(command.new_password)
        if self.password_hasher.verify(
            command.new_password,
            user.password.hashed_value,
        ):
            raise InvalidPasswordError(
                "New password must be different from the current password"
            )

        hashed = self.password_hasher.hash(command.new_password)
        user.update_password(Password(hashed))
        await self.user_repository.save(user)
        await self.refresh_token_repository.revoke_all_for_user(
            user.id,
            at=datetime.now(timezone.utc),
        )
