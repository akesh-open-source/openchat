"""add optional email to profiles

Revision ID: 0003_profiles_email
Revises: 0002_create_profiles
Create Date: 2026-09-15 01:30:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_profiles_email"
down_revision: Union[str, Sequence[str], None] = "0002_create_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "profiles",
        sa.Column("email", sa.String(length=254), nullable=True),
    )
    op.create_index("ix_profiles_email", "profiles", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_profiles_email", table_name="profiles")
    op.drop_column("profiles", "email")
