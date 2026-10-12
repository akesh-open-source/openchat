from __future__ import annotations

from enum import StrEnum


class MembershipRole(StrEnum):
    """Role within a conversation. Direct chats use member for both sides."""

    MEMBER = "member"
    ADMIN = "admin"
