from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.auth.application.commands.login_user import LoginUserCommand
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.device_repository import DeviceRepository
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.session_repository import SessionRepository
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.token_issuer import TokenIssuer, TokenPair
from app.auth.domain.entities.device import Device
from app.auth.domain.entities.refresh_token import RefreshToken, new_refresh_family_id
from app.auth.domain.entities.session import Session
from app.auth.domain.exceptions import InvalidCredentialsError
from app.auth.domain.value_objects.email import Email
from app.auth.infrastructure.security.token_hash import hash_token


@dataclass(slots=True)
class LoginService:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_issuer: TokenIssuer
    refresh_token_repository: RefreshTokenRepository
    device_repository: DeviceRepository
    session_repository: SessionRepository
    refresh_token_expire_days: int

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

        device = await self.device_repository.get_by_user_and_client_id(
            user.id,
            command.device_id,
        )
        if device is None:
            device = Device.create(
                user_id=user.id,
                client_device_id=command.device_id,
                name=command.device_name,
                user_agent=command.user_agent,
            )
        else:
            device.touch(
                name=command.device_name,
                user_agent=command.user_agent,
            )
        await self.device_repository.save(device)

        # Session must exist before access JWT is issued (access embeds sid).
        session = Session.create(
            user_id=user.id,
            device_id=device.id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.refresh_token_expire_days),
            ip_address=command.ip_address,
        )
        await self.session_repository.save(session)

        tokens = self.token_issuer.issue_tokens(
            user.id,
            user.email.value,
            session_id=session.id,
        )
        session.touch(expires_at=tokens.refresh_expires_at)
        await self.session_repository.save(session)

        await self.refresh_token_repository.save(
            RefreshToken.create(
                token_id=tokens.refresh_jti,
                user_id=user.id,
                token_hash=hash_token(tokens.refresh_token),
                family_id=new_refresh_family_id(),
                expires_at=tokens.refresh_expires_at,
                session_id=session.id,
            )
        )
        return tokens
