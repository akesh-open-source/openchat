from __future__ import annotations

from dataclasses import dataclass

from app.users.application.commands.create_profile import CreateProfileCommand
from app.users.application.ports.repositories.profile_repository import (
    ProfileRepository,
)
from app.users.domain.entities.profile import Profile
from app.users.domain.value_objects.display_name import DisplayName


@dataclass(frozen=True, slots=True)
class CreateProfileResult:
    profile: Profile
    created: bool


@dataclass(slots=True)
class CreateProfileService:
    profile_repository: ProfileRepository

    async def create(self, command: CreateProfileCommand) -> CreateProfileResult:
        existing = await self.profile_repository.get_by_user_id(command.user_id)
        if existing is not None:
            return CreateProfileResult(profile=existing, created=False)

        profile = Profile.create(
            user_id=command.user_id,
            display_name=DisplayName(command.display_name),
            email=command.email,
        )
        await self.profile_repository.save(profile)
        return CreateProfileResult(profile=profile, created=True)
