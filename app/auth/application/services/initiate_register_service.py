from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

from app.auth.application.commands.initiate_register import InitiateRegisterCommand
from app.auth.application.ports.email_sender import EmailSender
from app.auth.application.ports.email_template_renderer import EmailTemplateRenderer
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.pending_registration_store import (
    PendingRegistration,
    PendingRegistrationStore,
)
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.domain.exceptions import UserAlreadyExistsError
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password

logger = logging.getLogger(__name__)

_GENERIC_DETAIL = (
    "If this email can be used to register, a verification link has been sent."
)


@dataclass(frozen=True, slots=True)
class InitiateRegisterResult:
    detail: str
    registration_token: str | None = None


@dataclass(slots=True)
class InitiateRegisterService:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    pending_store: PendingRegistrationStore
    email_sender: EmailSender
    template_renderer: EmailTemplateRenderer
    app_name: str
    registration_verify_url_base: str
    registration_token_expire_minutes: int

    async def initiate(
        self,
        command: InitiateRegisterCommand,
    ) -> InitiateRegisterResult:
        email = Email(command.email)
        display_name = DisplayName(command.display_name)
        Password.validate_plain(command.password)

        existing = await self.user_repository.get_by_email(email.value)
        if existing is not None:
            # Same response shape — do not reveal that the email is taken via timing alone
            # is hard; still raise conflict so clients can correct typos.
            raise UserAlreadyExistsError(
                f"User with email {email.value} already exists"
            )

        password_hash = self.password_hasher.hash(command.password)
        token = secrets.token_urlsafe(32)
        await self.pending_store.save(
            token,
            PendingRegistration(
                email=email.value,
                password_hash=password_hash,
                display_name=display_name.value,
            ),
            ttl_seconds=self.registration_token_expire_minutes * 60,
        )
        await self._send_verification_email(
            email=email.value,
            display_name=display_name.value,
            token=token,
        )
        return InitiateRegisterResult(
            detail=_GENERIC_DETAIL,
            registration_token=token,
        )

    async def _send_verification_email(
        self,
        *,
        email: str,
        display_name: str,
        token: str,
    ) -> None:
        verify_link = (
            f"{self.registration_verify_url_base.rstrip('/')}"
            f"?{urlencode({'token': token})}"
        )
        rendered = self.template_renderer.render_register_verification(
            app_name=self.app_name,
            email=email,
            display_name=display_name,
            verify_link=verify_link,
            verify_token=token,
            expires_minutes=self.registration_token_expire_minutes,
        )
        try:
            await self.email_sender.send(
                to=email,
                subject=rendered.subject,
                text_body=rendered.text_body,
                html_body=rendered.html_body,
            )
        except Exception:
            logger.exception("Failed to send registration verification email to %s", email)
