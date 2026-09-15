from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetProfileCommand:
    user_id: UUID
