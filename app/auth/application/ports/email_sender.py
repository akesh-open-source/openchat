from __future__ import annotations

from typing import Protocol


class EmailSender(Protocol):
    """Port for outbound transactional email delivery."""

    async def send(
        self,
        *,
        to: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        """Send an email. Raises on delivery failure."""
        ...
