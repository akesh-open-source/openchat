from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.ports.email_sender import EmailSender
from app.auth.application.ports.email_template_renderer import EmailTemplateRenderer
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.pending_registration_store import PendingRegistrationStore
from app.auth.application.ports.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.ports.token_issuer import TokenIssuer
from app.auth.application.services.change_password_service import ChangePasswordService
from app.auth.application.services.complete_register_service import CompleteRegisterService
from app.auth.application.services.forgot_password_service import ForgotPasswordService
from app.auth.application.services.initiate_register_service import InitiateRegisterService
from app.auth.application.services.login_service import LoginService
from app.auth.application.services.refresh_token_service import RefreshTokenService
from app.auth.application.services.reset_password_service import ResetPasswordService
from app.auth.config.settings import settings
from app.auth.infrastructure.email.smtp_email_sender import SmtpEmailSender
from app.auth.infrastructure.email.template_renderer import JinjaEmailTemplateRenderer
from app.auth.infrastructure.persistence.postgres.session import get_session
from app.auth.infrastructure.persistence.postgres.refresh_token_repository import (
    PostgresRefreshTokenRepository,
)
from app.auth.infrastructure.persistence.postgres.user_repository import (
    PostgresUserRepository,
)
from app.auth.infrastructure.persistence.redis.client import get_redis
from app.auth.infrastructure.persistence.redis.pending_registration_store import (
    RedisPendingRegistrationStore,
)
from app.auth.infrastructure.security.jwt_token_issuer import JwtTokenIssuer
from app.auth.infrastructure.security.password_hasher import Argon2PasswordHasher
from app.auth.infrastructure.security.pem import load_pem
from app.auth.security.authentication import extract_bearer_token

_password_hasher = Argon2PasswordHasher()
_token_issuer = JwtTokenIssuer(
    private_key=load_pem(
        inline=settings.jwt_private_key,
        path=settings.jwt_private_key_path,
        name="private key",
    ),
    public_key=load_pem(
        inline=settings.jwt_public_key,
        path=settings.jwt_public_key_path,
        name="public key",
    ),
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.access_token_expire_minutes,
    refresh_token_expire_days=settings.refresh_token_expire_days,
    password_reset_token_expire_minutes=settings.password_reset_token_expire_minutes,
)
_email_sender = SmtpEmailSender(
    host=settings.smtp_host,
    port=settings.smtp_port,
    username=settings.smtp_username,
    password=settings.smtp_password,
    use_tls=settings.smtp_use_tls,
    use_ssl=settings.smtp_use_ssl,
    from_email=settings.smtp_from_email,
    from_name=settings.smtp_from_name,
)
_email_template_renderer = JinjaEmailTemplateRenderer()


def get_password_hasher() -> PasswordHasher:
    return _password_hasher


def get_token_issuer() -> TokenIssuer:
    return _token_issuer


def get_current_user_id(
    request: Request,
    token_issuer: Annotated[TokenIssuer, Depends(get_token_issuer)],
) -> UUID:
    """Require a valid Bearer access token; return the subject user id."""
    token = extract_bearer_token(request)
    return token_issuer.verify_access_token(token)


def get_email_sender() -> EmailSender:
    return _email_sender


def get_email_template_renderer() -> EmailTemplateRenderer:
    return _email_template_renderer


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return PostgresUserRepository(session)


def get_refresh_token_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RefreshTokenRepository:
    return PostgresRefreshTokenRepository(session)


def get_pending_registration_store() -> PendingRegistrationStore:
    return RedisPendingRegistrationStore(get_redis())


def get_initiate_register_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    pending_store: Annotated[
        PendingRegistrationStore,
        Depends(get_pending_registration_store),
    ],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    template_renderer: Annotated[
        EmailTemplateRenderer,
        Depends(get_email_template_renderer),
    ],
) -> InitiateRegisterService:
    return InitiateRegisterService(
        user_repository=user_repository,
        password_hasher=password_hasher,
        pending_store=pending_store,
        email_sender=email_sender,
        template_renderer=template_renderer,
        app_name=settings.app_name,
        registration_verify_url_base=settings.registration_verify_url_base,
        registration_token_expire_minutes=settings.registration_token_expire_minutes,
    )


def get_complete_register_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    pending_store: Annotated[
        PendingRegistrationStore,
        Depends(get_pending_registration_store),
    ],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    template_renderer: Annotated[
        EmailTemplateRenderer,
        Depends(get_email_template_renderer),
    ],
) -> CompleteRegisterService:
    return CompleteRegisterService(
        user_repository=user_repository,
        pending_store=pending_store,
        email_sender=email_sender,
        template_renderer=template_renderer,
        app_name=settings.app_name,
        login_url=settings.login_url,
    )


def get_login_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_issuer: Annotated[TokenIssuer, Depends(get_token_issuer)],
    refresh_token_repository: Annotated[
        RefreshTokenRepository,
        Depends(get_refresh_token_repository),
    ],
) -> LoginService:
    return LoginService(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
        refresh_token_repository=refresh_token_repository,
    )


def get_refresh_token_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repository: Annotated[
        RefreshTokenRepository,
        Depends(get_refresh_token_repository),
    ],
    token_issuer: Annotated[TokenIssuer, Depends(get_token_issuer)],
) -> RefreshTokenService:
    return RefreshTokenService(
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
        token_issuer=token_issuer,
    )


def get_forgot_password_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_issuer: Annotated[TokenIssuer, Depends(get_token_issuer)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    template_renderer: Annotated[
        EmailTemplateRenderer,
        Depends(get_email_template_renderer),
    ],
) -> ForgotPasswordService:
    return ForgotPasswordService(
        user_repository=user_repository,
        token_issuer=token_issuer,
        email_sender=email_sender,
        template_renderer=template_renderer,
        app_name=settings.app_name,
        password_reset_url_base=settings.password_reset_url_base,
        password_reset_token_expire_minutes=settings.password_reset_token_expire_minutes,
    )


def get_reset_password_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_issuer: Annotated[TokenIssuer, Depends(get_token_issuer)],
    refresh_token_repository: Annotated[
        RefreshTokenRepository,
        Depends(get_refresh_token_repository),
    ],
) -> ResetPasswordService:
    return ResetPasswordService(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
        refresh_token_repository=refresh_token_repository,
    )


def get_change_password_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    refresh_token_repository: Annotated[
        RefreshTokenRepository,
        Depends(get_refresh_token_repository),
    ],
) -> ChangePasswordService:
    return ChangePasswordService(
        user_repository=user_repository,
        password_hasher=password_hasher,
        refresh_token_repository=refresh_token_repository,
    )
