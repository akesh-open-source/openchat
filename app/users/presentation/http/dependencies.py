from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.application.ports.repositories.profile_repository import (
    ProfileRepository,
)
from app.users.application.services.create_profile_service import CreateProfileService
from app.users.application.services.get_profile_service import GetProfileService
from app.users.application.services.lookup_profile_service import LookupProfileService
from app.users.application.services.update_profile_service import UpdateProfileService
from app.users.infrastructure.persistence.postgres.profile_repository import (
    PostgresProfileRepository,
)
from app.users.infrastructure.persistence.postgres.session import get_session
from app.users.security.authentication import (
    extract_bearer_token,
    verify_access_token,
)


def get_profile_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileRepository:
    return PostgresProfileRepository(session)


def get_create_profile_service(
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> CreateProfileService:
    return CreateProfileService(profile_repository=profile_repository)


def get_get_profile_service(
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> GetProfileService:
    return GetProfileService(profile_repository=profile_repository)


def get_update_profile_service(
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> UpdateProfileService:
    return UpdateProfileService(profile_repository=profile_repository)


def get_lookup_profile_service(
    profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> LookupProfileService:
    return LookupProfileService(profile_repository=profile_repository)


def get_current_user_id(request: Request) -> UUID:
    """Require a valid Bearer access token; return subject user id."""
    token = extract_bearer_token(request)
    return verify_access_token(token)
