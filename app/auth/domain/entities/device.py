from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.auth.domain.ids import new_uuid7


@dataclass(slots=True)
class Device:
    """A client device belonging to a user (stable client_device_id)."""

    id: UUID
    user_id: UUID
    client_device_id: str
    name: str | None
    user_agent: str | None
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime

    @classmethod
    def create(
        cls,
        *,
        user_id: UUID,
        client_device_id: str,
        name: str | None = None,
        user_agent: str | None = None,
    ) -> Device:
        now = datetime.now(timezone.utc)
        return cls(
            id=new_uuid7(),
            user_id=user_id,
            client_device_id=client_device_id.strip(),
            name=name.strip() if name else None,
            user_agent=user_agent.strip() if user_agent else None,
            created_at=now,
            updated_at=now,
            last_seen_at=now,
        )

    def touch(
        self,
        *,
        name: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        self.last_seen_at = now
        self.updated_at = now
        if name is not None and name.strip():
            self.name = name.strip()
        if user_agent is not None and user_agent.strip():
            self.user_agent = user_agent.strip()
