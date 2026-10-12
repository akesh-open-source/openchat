from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetOrCreateDirectConversationCommand:
    """Caller wants a 1:1 chat with peer_user_id (caller is user_id)."""

    user_id: UUID
    peer_user_id: UUID
    access_token: str
