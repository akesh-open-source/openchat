from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.auth.domain.ids import new_uuid7
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password


@dataclass(slots=True)
class User:
    """User aggregate root."""

    id: UUID
    email: Email
    display_name: DisplayName
    password: Password
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        email: Email,
        display_name: DisplayName,
        password: Password,
    ) -> User:
        now = datetime.now(timezone.utc)
        return cls(
            id=new_uuid7(),
            email=email,
            display_name=display_name,
            password=password,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

    def update_password(self, password: Password) -> None:
        self.password = password
        self.updated_at = datetime.now(timezone.utc)

    def update_display_name(self, display_name: DisplayName) -> None:
        self.display_name = display_name
        self.updated_at = datetime.now(timezone.utc)
