from __future__ import annotations

from pathlib import Path

import pytest

from app.gateway.security.pem import load_pem


def test_load_pem_inline() -> None:
    assert load_pem(inline="-----BEGIN-----\nabc") == "-----BEGIN-----\nabc"


def test_load_pem_from_path(tmp_path: Path) -> None:
    path = tmp_path / "public.pem"
    path.write_text("pem-bytes\n", encoding="utf-8")
    assert load_pem(path=str(path)) == "pem-bytes"


def test_load_pem_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        load_pem(path=str(tmp_path / "nope.pem"), name="public key")


def test_load_pem_required() -> None:
    with pytest.raises(ValueError, match="required"):
        load_pem()
