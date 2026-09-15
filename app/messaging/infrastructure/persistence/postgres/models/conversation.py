from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.messaging.infrastructure.persistence.postgres.base import Base


class ConversationModel(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint(
            "direct_user_a_id",
            "direct_user_b_id",
            name="uq_conversations_direct_pair",
        ),
        CheckConstraint(
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
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    # Sorted auth user ids for direct chats; both NULL for group.
    direct_user_a_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        index=True,
    )
    direct_user_b_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        index=True,
    )
    next_sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
