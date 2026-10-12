from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from app.messaging.domain.exceptions import InvalidCursorError


@dataclass(frozen=True, slots=True)
class MessageListCursor:
    """Keyset cursor: history order is ``sequence ASC`` (contiguous pages)."""

    sequence: int

    def encode(self) -> str:
        payload = {"sequence": self.sequence}
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @classmethod
    def decode(cls, value: str) -> MessageListCursor:
        try:
            padded = value + "=" * (-len(value) % 4)
            raw = base64.urlsafe_b64decode(padded.encode("ascii"))
            payload = json.loads(raw.decode("utf-8"))
            sequence = int(payload["sequence"])
            if sequence < 1:
                raise ValueError("sequence must be >= 1")
            return cls(sequence=sequence)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise InvalidCursorError("Invalid pagination cursor") from exc
