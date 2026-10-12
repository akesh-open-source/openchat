from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ChangePasswordCommand:
    user_id: UUID
    current_password: str
    new_password: str