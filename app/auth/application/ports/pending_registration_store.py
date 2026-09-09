from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PendingRegistration:
    email: str
    password_hash: str
    display_name: str


class PendingRegistrationStore(Protocol):
    """Port for temporary registration payloads awaiting email verification."""

    async def save(
        self,
        token: str,
        pending: PendingRegistration,
        *,
        ttl_seconds: int,
    ) -> None:
        ...

    async def get(self, token: str) -> PendingRegistration | None:
        ...

    async def delete(self, token: str) -> None:
        ...
