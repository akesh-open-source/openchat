from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.auth.application.ports.email_template_renderer import RenderedEmail

_TEMPLATES_ROOT = Path(__file__).resolve().parent / "templates"


class JinjaEmailTemplateRenderer:
    """Renders auth transactional emails from Jinja2 HTML/text templates."""

    def __init__(self, templates_root: Path | None = None) -> None:
        root = templates_root or _TEMPLATES_ROOT
        self._env = Environment(
            loader=FileSystemLoader(
                [
                    str(root / "html"),
                    str(root / "text"),
                ]
            ),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

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
        context = {
            "app_name": app_name,
            "email": email,
            "display_name": display_name,
            "reset_link": reset_link,
            "reset_token": reset_token,
            "expires_minutes": expires_minutes,
        }
        return RenderedEmail(
            subject=f"Reset your {app_name} password",
            text_body=self._env.get_template("password_reset.txt").render(context),
            html_body=self._env.get_template("password_reset.html").render(context),
        )

    def render_register_user(
        self,
        *,
        app_name: str,
        email: str,
        display_name: str,
        login_url: str,
    ) -> RenderedEmail:
        context = {
            "app_name": app_name,
            "email": email,
            "display_name": display_name,
            "login_url": login_url,
        }
        return RenderedEmail(
            subject=f"Welcome to {app_name}",
            text_body=self._env.get_template("register_user.txt").render(context),
            html_body=self._env.get_template("register_user.html").render(context),
        )
