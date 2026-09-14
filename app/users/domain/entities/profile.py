from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.users.domain.value_objects.display_name import DisplayName


@dataclass(slots=True)
class Profile:
    """User profile aggregate (identity owned by auth; profile owned by users)."""

    user_id: UUID
    display_name: DisplayName
    created_at: datetime
    updated_at: datetime
    bio: str | None = None
    avatar_url: str | None = None

    @classmethod
    def create(
        cls,
        *,
        user_id: UUID,
        display_name: DisplayName,
        bio: str | None = None,
        avatar_url: str | None = None,
    ) -> Profile:
        now = datetime.now(timezone.utc)
        return cls(
            user_id=user_id,
            display_name=display_name,
            bio=bio.strip() if bio and bio.strip() else None,
            avatar_url=avatar_url.strip() if avatar_url and avatar_url.strip() else None,
            created_at=now,
            updated_at=now,
        )

    def update_display_name(self, display_name: DisplayName) -> None:
        self.display_name = display_name
        self.updated_at = datetime.now(timezone.utc)

    def update_bio(self, bio: str | None) -> None:
        self.bio = bio.strip() if bio and bio.strip() else None
        self.updated_at = datetime.now(timezone.utc)

    def update_avatar_url(self, avatar_url: str | None) -> None:
        self.avatar_url = (
            avatar_url.strip() if avatar_url and avatar_url.strip() else None
        )
        self.updated_at = datetime.now(timezone.utc)
