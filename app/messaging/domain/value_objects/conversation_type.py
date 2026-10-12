from __future__ import annotations

from enum import StrEnum


class ConversationType(StrEnum):
    """Conversation kind: direct (1:1) now; group later."""

    DIRECT = "direct"
    GROUP = "group"
