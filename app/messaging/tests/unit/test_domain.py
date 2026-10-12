from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import SelfConversationError
from app.messaging.domain.value_objects.conversation_type import ConversationType
from app.messaging.domain.value_objects.membership_role import MembershipRole
from app.messaging.domain.value_objects.user_pair import sorted_user_pair


def test_sorted_user_pair_orders_ids() -> None:
    low = UUID("00000000-0000-0000-0000-000000000001")
    high = UUID("00000000-0000-0000-0000-000000000002")
    assert sorted_user_pair(high, low) == (low, high)
    assert sorted_user_pair(low, high) == (low, high)


def test_sorted_user_pair_rejects_self() -> None:
    user_id = uuid4()
    with pytest.raises(SelfConversationError):
        sorted_user_pair(user_id, user_id)


def test_conversation_create_direct_sorts_pair() -> None:
    low = UUID("00000000-0000-0000-0000-000000000001")
    high = UUID("00000000-0000-0000-0000-000000000002")
    conversation = Conversation.create_direct(user_a_id=high, user_b_id=low)

    assert conversation.type is ConversationType.DIRECT
    assert conversation.is_direct
    assert conversation.direct_user_a_id == low
    assert conversation.direct_user_b_id == high
    assert conversation.next_sequence == 0


def test_conversation_create_direct_rejects_self() -> None:
    user_id = uuid4()
    with pytest.raises(SelfConversationError):
        Conversation.create_direct(user_a_id=user_id, user_b_id=user_id)


def test_membership_create_defaults() -> None:
    conversation_id = uuid4()
    user_id = uuid4()
    membership = Membership.create(
        conversation_id=conversation_id,
        user_id=user_id,
    )
    assert membership.conversation_id == conversation_id
    assert membership.user_id == user_id
    assert membership.role is MembershipRole.MEMBER
