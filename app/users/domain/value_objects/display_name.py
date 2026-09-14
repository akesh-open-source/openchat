from __future__ import annotations

from dataclasses import dataclass

from app.users.domain.exceptions import InvalidDisplayNameError

_MIN_LENGTH = 3
_MAX_LENGTH = 30


@dataclass(frozen=True, slots=True)
class DisplayName:
    """Value object for display name."""

    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise InvalidDisplayNameError("Display name cannot be empty")

        if len(value) < _MIN_LENGTH or len(value) > _MAX_LENGTH:
            raise InvalidDisplayNameError(
                f"Display name must be between {_MIN_LENGTH} and {_MAX_LENGTH} characters"
            )

        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
