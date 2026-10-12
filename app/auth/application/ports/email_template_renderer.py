from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RenderedEmail:
    subject: str
    text_body: str
    html_body: str


class EmailTemplateRenderer(Protocol):
    """Port for rendering transactional email content from templates."""

    def render_password_reset(
        self,
        *,
        app_name: str,
        email: str,
        reset_link: str,
        reset_token: str,
        expires_minutes: int,
        display_name: str | None = None,
    ) -> RenderedEmail:
        ...

    def render_register_verification(
        self,
        *,
        app_name: str,
        email: str,
        display_name: str,
        verify_link: str,
        verify_token: str,
        expires_minutes: int,
    ) -> RenderedEmail:
        ...

    def render_register_user(
        self,
        *,
        app_name: str,
        email: str,
        display_name: str,
        login_url: str,
    ) -> RenderedEmail:
        ...
