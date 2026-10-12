from __future__ import annotations

import pytest

from app.auth.infrastructure.security.password_hasher import Argon2PasswordHasher


def test_hash_and_verify() -> None:
    hasher = Argon2PasswordHasher()
    hashed = hasher.hash("correct-horse-battery")
    assert hasher.verify("correct-horse-battery", hashed) is True
    assert hasher.verify("wrong-password", hashed) is False


def test_verify_invalid_hash_returns_false() -> None:
    hasher = Argon2PasswordHasher()
    assert hasher.verify("anything", "not-a-valid-argon2-hash") is False
