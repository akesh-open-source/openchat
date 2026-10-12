from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SendMessageCommand:
    user_id: UUID
    conversation_id: UUID
    client_message_id: str
    body: str
