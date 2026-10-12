"""Time-ordered entity identifiers (UUIDv7 via uuid6)."""

from __future__ import annotations

from uuid import UUID

import uuid6


def new_uuid7() -> UUID:
    """Generate a fast, time-sorted UUIDv7 primary key."""
    return uuid6.uuid7()
