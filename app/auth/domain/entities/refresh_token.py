from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.auth.domain.ids import new_uuid7


@dataclass(slots=True)
class RefreshToken:
    """Persisted refresh token (JWT jti maps to id), bound to a session."""

    id: UUID
    user_id: UUID
    token_hash: str
    family_id: UUID
    expires_at: datetime
    created_at: datetime
    session_id: UUID | None = None
    revoked_at: datetime | None = None
    replaced_by_id: UUID | None = None

    @classmethod
    def create(
        cls,
        *,
        token_id: UUID,
        user_id: UUID,
        token_hash: str,
        family_id: UUID,
        expires_at: datetime,
        session_id: UUID | None = None,
    ) -> RefreshToken:
        return cls(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
            session_id=session_id,
        )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def revoke(self, *, replaced_by_id: UUID | None = None) -> None:
        if self.revoked_at is None:
            self.revoked_at = datetime.now(timezone.utc)
        if replaced_by_id is not None:
            self.replaced_by_id = replaced_by_id


def new_refresh_family_id() -> UUID:
    return new_uuid7()
