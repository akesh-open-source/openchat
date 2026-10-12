from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class LookupProfileQuery:
    email: str | None = None
    user_id: UUID | None = None
