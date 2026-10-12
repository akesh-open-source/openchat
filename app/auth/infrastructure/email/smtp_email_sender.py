from __future__ import annotations

import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class SmtpEmailSender:
    """SMTP-backed email delivery using the standard library."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool,
        use_ssl: bool,
        from_email: str,
        from_name: str,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username or None
        self._password = password or None
        self._use_tls = use_tls
        self._use_ssl = use_ssl
        self._from_email = from_email
        self._from_name = from_name

    async def send(
        self,
        *,
        to: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        message = EmailMessage()
        message["From"] = f"{self._from_name} <{self._from_email}>"
        message["To"] = to
        message["Subject"] = subject
        message.set_content(text_body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        logger.info("Sending email via SMTP to=%s subject=%s", to, subject)
        await asyncio.to_thread(self._send_sync, message)

    def _send_sync(self, message: EmailMessage) -> None:
        if self._use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                self._host,
                self._port,
                context=context,
            ) as smtp:
                self._authenticate_and_send(smtp, message)
            return

        with smtplib.SMTP(self._host, self._port) as smtp:
            if self._use_tls:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
            self._authenticate_and_send(smtp, message)

    def _authenticate_and_send(
        self,
        smtp: smtplib.SMTP,
        message: EmailMessage,
    ) -> None:
        if self._username and self._password:
            smtp.login(self._username, self._password)
        smtp.send_message(message)
