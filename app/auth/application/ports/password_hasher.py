from __future__ import annotations

from typing import Protocol


class PasswordHasher(Protocol):
    """Port for hashing and verifying passwords."""

    def hash(self, password: str) -> str:
        ...

    def verify(self, password: str, password_hash: str) -> bool:
        ...
