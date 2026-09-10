from __future__ import annotations

from app.auth.infrastructure.security.token_hash import hash_token


def test_hash_token_is_sha256_hex() -> None:
    digest = hash_token("refresh-token-value")
    assert len(digest) == 64
    assert digest == hash_token("refresh-token-value")
    assert digest != hash_token("other-token")
