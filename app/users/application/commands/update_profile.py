from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UpdateProfileCommand:
    user_id: UUID
    fields_set: frozenset[str] = field(default_factory=frozenset)
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
