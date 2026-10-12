from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urlencode

from app.auth.application.commands.forgot_password import ForgotPasswordCommand
from app.auth.application.ports.email_sender import EmailSender
from app.auth.application.ports.email_template_renderer import EmailTemplateRenderer
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.token_issuer import TokenIssuer
from app.auth.domain.value_objects.email import Email

logger = logging.getLogger(__name__)

_GENERIC_DETAIL = (
    "If an account exists for this email, password reset instructions have been sent."
)


@dataclass(frozen=True, slots=True)
class ForgotPasswordResult:
    detail: str
    reset_token: str | None = None


@dataclass(slots=True)
class ForgotPasswordService:
    user_repository: UserRepository
    token_issuer: TokenIssuer
    email_sender: EmailSender
    template_renderer: EmailTemplateRenderer
    app_name: str
    password_reset_url_base: str
    password_reset_token_expire_minutes: int

    async def forgot_password(
        self,
        command: ForgotPasswordCommand,
    ) -> ForgotPasswordResult:
        email = Email(command.email)
        user = await self.user_repository.get_by_email(email.value)

        reset_token: str | None = None
        if user is not None and user.is_active:
            reset_token = self.token_issuer.issue_password_reset_token(
                user.id,
                user.email.value,
            )
            await self._send_reset_email(
                to=user.email.value,
                display_name=user.display_name.value,
                reset_token=reset_token,
            )

        return ForgotPasswordResult(detail=_GENERIC_DETAIL, reset_token=reset_token)

    async def _send_reset_email(
        self,
        *,
        to: str,
        display_name: str,
        reset_token: str,
    ) -> None:
        reset_link = (
            f"{self.password_reset_url_base.rstrip('/')}"
            f"?{urlencode({'token': reset_token})}"
        )
        rendered = self.template_renderer.render_password_reset(
            app_name=self.app_name,
            email=to,
            display_name=display_name,
            reset_link=reset_link,
            reset_token=reset_token,
            expires_minutes=self.password_reset_token_expire_minutes,
        )
        try:
            await self.email_sender.send(
                to=to,
                subject=rendered.subject,
                text_body=rendered.text_body,
                html_body=rendered.html_body,
            )
        except Exception:
            # Do not fail the HTTP response — avoids email/SMTP oracle leaks.
            logger.exception("Failed to send password reset email to %s", to)
