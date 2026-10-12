from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetConversationQuery:
    user_id: UUID
    conversation_id: UUID
    access_token: str
