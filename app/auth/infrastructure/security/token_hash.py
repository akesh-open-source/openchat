import hashlib


def hash_token(token: str) -> str:
    """SHA-256 hex digest of a raw token (store hash, never the token)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
