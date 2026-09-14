from __future__ import annotations

from dataclasses import dataclass

from app.users.application.commands.get_profile import GetProfileCommand
from app.users.application.ports.repositories.profile_repository import (
    ProfileRepository,
)
from app.users.domain.entities.profile import Profile
from app.users.domain.exceptions import ProfileNotFoundError


@dataclass(slots=True)
class GetProfileService:
    profile_repository: ProfileRepository

    async def get(self, command: GetProfileCommand) -> Profile:
        profile = await self.profile_repository.get_by_user_id(command.user_id)
        if profile is None:
            raise ProfileNotFoundError(f"Profile not found for user {command.user_id}")
        return profile
