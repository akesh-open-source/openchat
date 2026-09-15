from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RevokeSessionCommand:
    user_id: UUID
    session_id: UUID
