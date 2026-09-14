from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateProfileCommand:
    user_id: UUID
    display_name: str
    email: str | None = None
