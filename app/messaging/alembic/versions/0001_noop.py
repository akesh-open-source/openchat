"""noop initial revision

Revision ID: 0001_noop
Revises:
Create Date: 2026-09-15 11:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "0001_noop"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
