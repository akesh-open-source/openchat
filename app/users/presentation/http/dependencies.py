from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.application.ports.repositories.profile_repository import (
    ProfileRepository,
)
from app.users.application.services.create_profile_service import CreateProfileService
from app.users.infrastructure.persistence.postgres.profile_repository import (
    PostgresProfileRepository,
)
from app.users.infrastructure.persistence.postgres.session import get_session


def get_profile_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileRepository:
    return PostgresProfileRepository(session)


def get_create_profile_service(
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> CreateProfileService:
    return CreateProfileService(profile_repository=profile_repository)
