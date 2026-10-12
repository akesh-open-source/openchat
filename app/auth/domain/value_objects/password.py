from __future__ import annotations

from dataclasses import dataclass

from app.auth.domain.exceptions import InvalidPasswordError

_MIN_PLAIN_LENGTH = 8
_MAX_PLAIN_LENGTH = 128


@dataclass(frozen=True, slots=True)
class Password:
    """Value object wrapping a hashed password."""

    hashed_value: str

    def __post_init__(self) -> None:
        if not self.hashed_value:
            raise InvalidPasswordError("Hashed password cannot be empty")

    @staticmethod
    def validate_plain(plain: str) -> None:
        """Validate plaintext password strength before hashing."""
        if not plain:
            raise InvalidPasswordError("Password cannot be empty")

        if len(plain) < _MIN_PLAIN_LENGTH:
            raise InvalidPasswordError(
                f"Password must be at least {_MIN_PLAIN_LENGTH} characters"
            )

        if len(plain) > _MAX_PLAIN_LENGTH:
            raise InvalidPasswordError(
                f"Password must be at most {_MAX_PLAIN_LENGTH} characters"
            )

    def __str__(self) -> str:
        return self.hashed_value
