from __future__ import annotations

import logging
from dataclasses import dataclass

from app.auth.application.commands.complete_register import CompleteRegisterCommand
from app.auth.application.ports.email_sender import EmailSender
from app.auth.application.ports.email_template_renderer import EmailTemplateRenderer
from app.auth.application.ports.pending_registration_store import PendingRegistrationStore
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.users_client import UsersClient
from app.auth.domain.entities.user import User
from app.auth.domain.exceptions import InvalidTokenError, UserAlreadyExistsError
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CompleteRegisterService:
    user_repository: UserRepository
    pending_store: PendingRegistrationStore
    email_sender: EmailSender
    template_renderer: EmailTemplateRenderer
    users_client: UsersClient
    app_name: str
    login_url: str

    async def complete(self, command: CompleteRegisterCommand) -> User:
        pending = await self.pending_store.get(command.token)
        if pending is None:
            raise InvalidTokenError("Invalid or expired registration token")

        existing = await self.user_repository.get_by_email(pending.email)
        if existing is not None:
            await self.pending_store.delete(command.token)
            raise UserAlreadyExistsError(
                f"User with email {pending.email} already exists"
            )

        user = User.create(
            email=Email(pending.email),
            display_name=DisplayName(pending.display_name),
            password=Password(pending.password_hash),
        )
        await self.user_repository.save(user)
        await self.pending_store.delete(command.token)

        # Policy: registration succeeds even if users/email is down (log + continue).
        # Profile create is idempotent — safe to retry later.
        await self._create_users_profile(user)
        await self._send_welcome_email(user)
        return user

    async def _create_users_profile(self, user: User) -> None:
        try:
            await self.users_client.create_profile(
                user_id=user.id,
                display_name=user.display_name.value,
                email=user.email.value,
            )
        except Exception:
            logger.exception(
                "Failed to sync profile to users service for user_id=%s; "
                "auth user was created — retry create-profile later",
                user.id,
            )

    async def _send_welcome_email(self, user: User) -> None:
        rendered = self.template_renderer.render_register_user(
            app_name=self.app_name,
            email=user.email.value,
            display_name=user.display_name.value,
            login_url=self.login_url,
        )
        try:
            await self.email_sender.send(
                to=user.email.value,
                subject=rendered.subject,
                text_body=rendered.text_body,
                html_body=rendered.html_body,
            )
        except Exception:
            logger.exception(
                "Failed to send registration welcome email to %s",
                user.email.value,
            )
