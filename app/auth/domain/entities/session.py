from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.auth.domain.ids import new_uuid7


@dataclass(slots=True)
class Session:
    """An authenticated login session on a device (bound to refresh tokens)."""

    id: UUID
    user_id: UUID
    device_id: UUID
    expires_at: datetime
    created_at: datetime
    last_seen_at: datetime
    ip_address: str | None = None
    revoked_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        user_id: UUID,
        device_id: UUID,
        expires_at: datetime,
        ip_address: str | None = None,
    ) -> Session:
        now = datetime.now(timezone.utc)
        return cls(
            id=new_uuid7(),
            user_id=user_id,
            device_id=device_id,
            expires_at=expires_at,
            created_at=now,
            last_seen_at=now,
            ip_address=ip_address,
        )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_active(self) -> bool:
        if self.is_revoked:
            return False
        return self.expires_at > datetime.now(timezone.utc)

    def touch(self, *, expires_at: datetime | None = None) -> None:
        self.last_seen_at = datetime.now(timezone.utc)
        if expires_at is not None:
            self.expires_at = expires_at

    def revoke(self) -> None:
        if self.revoked_at is None:
            self.revoked_at = datetime.now(timezone.utc)
