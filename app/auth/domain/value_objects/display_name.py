from __future__ import annotations

from dataclasses import dataclass

from app.auth.domain.exceptions import InvalidDisplayNameError


@dataclass(frozen=True, slots=True)
class DisplayName:
    """Value object for display name."""

    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise InvalidDisplayNameError("Display name cannot be empty")

        if len(value) < 3 or len(value) > 30:
            raise InvalidDisplayNameError(
                "Display name must be between 3 and 30 characters"
            )

        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
