from __future__ import annotations

import pytest
from fastapi import Request

from app.auth.domain.exceptions import InvalidTokenError
from app.auth.security.authentication import extract_bearer_token


def _request(authorization: bytes | None) -> Request:
    headers = []
    if authorization is not None:
        headers.append((b"authorization", authorization))
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": headers,
        }
    )


def test_extract_bearer_token_success() -> None:
    assert extract_bearer_token(_request(b"Bearer abc.def.ghi")) == "abc.def.ghi"


def test_extract_bearer_token_missing_header() -> None:
    with pytest.raises(InvalidTokenError, match="Missing Authorization"):
        extract_bearer_token(_request(None))


@pytest.mark.parametrize(
    "value",
    [b"Basic abc", b"Bearer", b"Bearer   ", b"token-only"],
)
def test_extract_bearer_token_malformed(value: bytes) -> None:
    with pytest.raises(InvalidTokenError, match="Bearer"):
        extract_bearer_token(_request(value))
