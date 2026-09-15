"""create conversations and memberships tables

Revision ID: 0002_create_conversations_memberships
Revises: 0001_noop
Create Date: 2026-09-15 12:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_create_conversations_memberships"
down_revision: Union[str, Sequence[str], None] = "0001_noop"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("direct_user_a_id", sa.Uuid(), nullable=True),
        sa.Column("direct_user_b_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "("
            "type = 'direct' "
            "AND direct_user_a_id IS NOT NULL "
            "AND direct_user_b_id IS NOT NULL "
            "AND direct_user_a_id < direct_user_b_id"
            ") OR ("
            "type = 'group' "
            "AND direct_user_a_id IS NULL "
            "AND direct_user_b_id IS NULL"
            ")",
            name="ck_conversations_direct_pair",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "direct_user_a_id",
            "direct_user_b_id",
            name="uq_conversations_direct_pair",
        ),
    )
    op.create_index(
        "ix_conversations_direct_user_a_id",
        "conversations",
        ["direct_user_a_id"],
        unique=False,
    )
    op.create_index(
        "ix_conversations_direct_user_b_id",
        "conversations",
        ["direct_user_b_id"],
        unique=False,
    )

    op.create_table(
        "memberships",
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("conversation_id", "user_id"),
    )
    op.create_index(
        "ix_memberships_user_id",
        "memberships",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_memberships_user_id", table_name="memberships")
    op.drop_table("memberships")
    op.drop_index("ix_conversations_direct_user_b_id", table_name="conversations")
    op.drop_index("ix_conversations_direct_user_a_id", table_name="conversations")
    op.drop_table("conversations")
