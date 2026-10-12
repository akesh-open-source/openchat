from __future__ import annotations

from dataclasses import dataclass

from app.users.application.commands.update_profile import UpdateProfileCommand
from app.users.application.ports.repositories.profile_repository import (
    ProfileRepository,
)
from app.users.domain.entities.profile import Profile
from app.users.domain.exceptions import InvalidDisplayNameError, ProfileNotFoundError
from app.users.domain.value_objects.display_name import DisplayName


@dataclass(slots=True)
class UpdateProfileService:
    profile_repository: ProfileRepository

    async def update(self, command: UpdateProfileCommand) -> Profile:
        profile = await self.profile_repository.get_by_user_id(command.user_id)
        if profile is None:
            raise ProfileNotFoundError(f"Profile not found for user {command.user_id}")

        if "display_name" in command.fields_set:
            if command.display_name is None:
                raise InvalidDisplayNameError("Display name cannot be empty")
            profile.update_display_name(DisplayName(command.display_name))
        if "bio" in command.fields_set:
            profile.update_bio(command.bio)
        if "avatar_url" in command.fields_set:
            profile.update_avatar_url(command.avatar_url)

        await self.profile_repository.save(profile)
        return profile
