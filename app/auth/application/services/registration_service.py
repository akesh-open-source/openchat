from __future__ import annotations

import logging
from dataclasses import dataclass

from app.auth.application.commands.register_user import RegisterUserCommand
from app.auth.application.ports.email_sender import EmailSender
from app.auth.application.ports.email_template_renderer import EmailTemplateRenderer
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.domain.entities.user import User
from app.auth.domain.exceptions import UserAlreadyExistsError
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RegistrationService:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    email_sender: EmailSender
    template_renderer: EmailTemplateRenderer
    app_name: str
    login_url: str

    async def register(self, command: RegisterUserCommand) -> User:
        email = Email(command.email)
        display_name = DisplayName(command.display_name)
        Password.validate_plain(command.password)

        existing_user = await self.user_repository.get_by_email(email.value)
        if existing_user is not None:
            raise UserAlreadyExistsError(
                f"User with email {email.value} already exists"
            )

        hashed_password = self.password_hasher.hash(command.password)
        user = User.create(
            email=email,
            display_name=display_name,
            password=Password(hashed_password),
        )
        await self.user_repository.save(user)
        await self._send_welcome_email(user)
        return user

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
