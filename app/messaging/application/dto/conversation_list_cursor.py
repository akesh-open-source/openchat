from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.messaging.domain.exceptions import InvalidCursorError


@dataclass(frozen=True, slots=True)
class ConversationListCursor:
    """Keyset cursor: order is (updated_at DESC, id DESC)."""

    updated_at: datetime
    id: UUID

    def encode(self) -> str:
        payload = {
            "updated_at": self.updated_at.isoformat(),
            "id": str(self.id),
        }
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @classmethod
    def decode(cls, value: str) -> ConversationListCursor:
        try:
            padded = value + "=" * (-len(value) % 4)
            raw = base64.urlsafe_b64decode(padded.encode("ascii"))
            payload = json.loads(raw.decode("utf-8"))
            return cls(
                updated_at=datetime.fromisoformat(payload["updated_at"]),
                id=UUID(payload["id"]),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise InvalidCursorError("Invalid pagination cursor") from exc
