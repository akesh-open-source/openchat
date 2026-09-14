from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.users.application.commands.get_profile import GetProfileCommand
from app.users.application.commands.update_profile import UpdateProfileCommand
from app.users.application.services.get_profile_service import GetProfileService
from app.users.application.services.update_profile_service import UpdateProfileService
from app.users.domain.entities.profile import Profile
from app.users.presentation.http.dependencies import (
    get_current_user_id,
    get_get_profile_service,
    get_update_profile_service,
)
from app.users.presentation.http.schemas.profiles import (
    ProfileResponse,
    UpdateProfileRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["profiles"],
)


def _to_response(profile: Profile) -> ProfileResponse:
    return ProfileResponse(
        user_id=profile.user_id,
        display_name=profile.display_name.value,
        email=profile.email,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_profile(
    user_id: UUID = Depends(get_current_user_id),
    service: GetProfileService = Depends(get_get_profile_service),
) -> ProfileResponse:
    profile = await service.get(GetProfileCommand(user_id=user_id))
    return _to_response(profile)


@router.get(
    "/{user_id}",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    user_id: UUID,
    _: UUID = Depends(get_current_user_id),
    service: GetProfileService = Depends(get_get_profile_service),
) -> ProfileResponse:
    profile = await service.get(GetProfileCommand(user_id=user_id))
    return _to_response(profile)


@router.patch(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def update_my_profile(
    request: UpdateProfileRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: UpdateProfileService = Depends(get_update_profile_service),
) -> ProfileResponse:
    # Only PATCH /users/me — callers cannot update another user's profile.
    fields_set = frozenset(request.model_dump(exclude_unset=True).keys())
    profile = await service.update(
        UpdateProfileCommand(
            user_id=user_id,
            fields_set=fields_set,
            display_name=request.display_name,
            bio=request.bio,
            avatar_url=request.avatar_url,
        )
    )
    return _to_response(profile)
