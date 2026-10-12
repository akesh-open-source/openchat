from __future__ import annotations

import re
from dataclasses import dataclass

from app.auth.domain.exceptions import InvalidEmailError

_EMAIL_PATTERN = re.compile(
    r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)


@dataclass(frozen=True, slots=True)
class Email:
    """Value object for email address."""

    value: str

    def __post_init__(self) -> None:
        value = self.value.strip().lower()

        if not value:
            raise InvalidEmailError("Email cannot be empty")

        if len(value) > 254 or not _EMAIL_PATTERN.match(value):
            raise InvalidEmailError(f"Invalid email: {self.value}")

        local, _, domain = value.partition("@")
        if not local or not domain:
            raise InvalidEmailError(f"Invalid email: {self.value}")

        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
