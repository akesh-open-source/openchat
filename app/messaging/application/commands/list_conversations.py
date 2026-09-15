from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ListConversationsQuery:
    user_id: UUID
    access_token: str
    limit: int = 20
    cursor: str | None = None
