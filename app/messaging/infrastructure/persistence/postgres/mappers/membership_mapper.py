from __future__ import annotations

from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.infrastructure.persistence.postgres.models.membership import (
    MembershipModel,
)


def to_domain(model: MembershipModel) -> Membership:
    return Membership(
        conversation_id=model.conversation_id,
        user_id=model.user_id,
        role=MembershipRole(model.role),
        joined_at=model.joined_at,
    )


def to_model(membership: Membership) -> MembershipModel:
    return MembershipModel(
        conversation_id=membership.conversation_id,
        user_id=membership.user_id,
        role=membership.role.value,
        joined_at=membership.joined_at,
    )
