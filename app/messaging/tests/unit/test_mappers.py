from __future__ import annotations

from uuid import UUID, uuid4

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.infrastructure.persistence.postgres.mappers.conversation_mapper import (
    to_domain as conversation_to_domain,
)
from app.messaging.infrastructure.persistence.postgres.mappers.conversation_mapper import (
    to_model as conversation_to_model,
)
from app.messaging.infrastructure.persistence.postgres.mappers.membership_mapper import (
    to_domain as membership_to_domain,
)
from app.messaging.infrastructure.persistence.postgres.mappers.membership_mapper import (
    to_model as membership_to_model,
)


def test_conversation_mapper_roundtrip() -> None:
    low = UUID("00000000-0000-0000-0000-000000000001")
    high = UUID("00000000-0000-0000-0000-000000000002")
    conversation = Conversation.create_direct(user_a_id=high, user_b_id=low)

    model = conversation_to_model(conversation)
    restored = conversation_to_domain(model)

    assert restored.id == conversation.id
    assert restored.type == conversation.type
    assert restored.direct_user_a_id == low
    assert restored.direct_user_b_id == high
    assert restored.created_at == conversation.created_at
    assert restored.updated_at == conversation.updated_at


def test_membership_mapper_roundtrip() -> None:
    membership = Membership.create(
        conversation_id=uuid4(),
        user_id=uuid4(),
        role=MembershipRole.ADMIN,
    )
    model = membership_to_model(membership)
    restored = membership_to_domain(model)

    assert restored.conversation_id == membership.conversation_id
    assert restored.user_id == membership.user_id
    assert restored.role is MembershipRole.ADMIN
    assert restored.joined_at == membership.joined_at
