from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.users.application.commands.create_profile import CreateProfileCommand
from app.users.application.services.create_profile_service import CreateProfileService
from app.users.presentation.http.dependencies import get_create_profile_service
from app.users.presentation.http.schemas.internal_profiles import (
    CreateProfileRequest,
    CreateProfileResponse,
)

router = APIRouter(
    prefix="/internal",
    tags=["internal"],
)


@router.post(
    "/profiles",
    response_model=CreateProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def create_profile(
    request: CreateProfileRequest,
    service: CreateProfileService = Depends(get_create_profile_service),
) -> CreateProfileResponse:
    """Idempotent profile create for auth (Compose-internal; not via gateway)."""
    result = await service.create(
        CreateProfileCommand(
            user_id=request.user_id,
            display_name=request.display_name,
            email=str(request.email) if request.email is not None else None,
        )
    )
    profile = result.profile
    return CreateProfileResponse(
        user_id=profile.user_id,
        display_name=profile.display_name.value,
        email=profile.email,
        created=result.created,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
