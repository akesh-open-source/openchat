from __future__ import annotations

from enum import StrEnum


class MessageStatus(StrEnum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
