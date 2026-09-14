from __future__ import annotations

from dataclasses import dataclass

from app.users.application.commands.lookup_profile import LookupProfileQuery
from app.users.application.ports.repositories.profile_repository import (
    ProfileRepository,
)
from app.users.domain.entities.profile import Profile
from app.users.domain.exceptions import DomainError, ProfileNotFoundError


@dataclass(slots=True)
class LookupProfileService:
    profile_repository: ProfileRepository

    async def lookup(self, query: LookupProfileQuery) -> Profile:
        has_email = bool(query.email and query.email.strip())
        has_user_id = query.user_id is not None
        if has_email == has_user_id:
            raise DomainError("Provide exactly one of email or user_id")

        if has_user_id:
            profile = await self.profile_repository.get_by_user_id(query.user_id)  # type: ignore[arg-type]
        else:
            email = query.email.strip().lower()  # type: ignore[union-attr]
            profile = await self.profile_repository.get_by_email(email)

        if profile is None:
            raise ProfileNotFoundError("Profile not found")
        return profile
