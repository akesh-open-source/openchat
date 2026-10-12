from __future__ import annotations

from pathlib import Path


def load_pem(*, inline: str = "", path: str = "", name: str = "key") -> str:
    """Load a PEM from an inline string or a file path (path wins if both set)."""
    if path.strip():
        pem_path = Path(path).expanduser()
        if not pem_path.is_file():
            raise ValueError(f"JWT {name} file not found: {pem_path}")
        pem = pem_path.read_text(encoding="utf-8").strip()
        if not pem:
            raise ValueError(f"JWT {name} file is empty: {pem_path}")
        return pem

    if inline.strip():
        return inline.strip().replace("\\n", "\n")

    raise ValueError(
        f"JWT {name} is required: set the inline PEM or a filesystem path"
    )
