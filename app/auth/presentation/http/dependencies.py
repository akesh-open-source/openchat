from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.application.services.registration_service import RegistrationService
from app.auth.infrastructure.persistence.postgres.session import get_session
from app.auth.infrastructure.persistence.postgres.user_repository import (
    PostgresUserRepository,
)
from app.auth.infrastructure.security.password_hasher import Argon2PasswordHasher

_password_hasher = Argon2PasswordHasher()


def get_password_hasher() -> PasswordHasher:
    return _password_hasher


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return PostgresUserRepository(session)


def get_registration_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> RegistrationService:
    return RegistrationService(
        user_repository=user_repository,
        password_hasher=password_hasher,
    )