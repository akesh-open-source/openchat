from __future__ import annotations

from pathlib import Path

import pytest

from app.auth.infrastructure.security.pem import load_pem


def test_load_pem_inline() -> None:
    pem = "-----BEGIN PUBLIC KEY-----\nabc\n-----END PUBLIC KEY-----"
    assert load_pem(inline=pem) == pem


def test_load_pem_inline_literal_newlines() -> None:
    result = load_pem(inline="line1\\nline2")
    assert result == "line1\nline2"


def test_load_pem_from_path(tmp_path: Path) -> None:
    path = tmp_path / "key.pem"
    path.write_text("  PEM-CONTENT  \n", encoding="utf-8")
    assert load_pem(path=str(path)) == "PEM-CONTENT"


def test_load_pem_path_wins_over_inline(tmp_path: Path) -> None:
    path = tmp_path / "key.pem"
    path.write_text("from-file", encoding="utf-8")
    assert load_pem(inline="from-inline", path=str(path)) == "from-file"


def test_load_pem_missing_path_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="file not found"):
        load_pem(path=str(tmp_path / "missing.pem"))


def test_load_pem_empty_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "empty.pem"
    path.write_text("   \n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_pem(path=str(path))


def test_load_pem_requires_source() -> None:
    with pytest.raises(ValueError, match="required"):
        load_pem()
