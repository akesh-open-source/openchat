from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ListMessagesQuery:
    user_id: UUID
    conversation_id: UUID
    limit: int = 50
    cursor: str | None = None
