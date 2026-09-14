from __future__ import annotations

from uuid import uuid4

import pytest

from app.users.domain.entities.profile import Profile
from app.users.domain.exceptions import InvalidDisplayNameError
from app.users.domain.value_objects.display_name import DisplayName


def test_display_name_normalizes() -> None:
    assert DisplayName("  Alice  ").value == "Alice"


@pytest.mark.parametrize("value", ["", "ab", "x" * 31])
def test_display_name_rejects_invalid(value: str) -> None:
    with pytest.raises(InvalidDisplayNameError):
        DisplayName(value)


def test_profile_create_and_update() -> None:
    user_id = uuid4()
    profile = Profile.create(
        user_id=user_id,
        display_name=DisplayName("Alice"),
        bio="  hello  ",
    )
    assert profile.user_id == user_id
    assert profile.display_name.value == "Alice"
    assert profile.bio == "hello"
    assert profile.avatar_url is None

    before = profile.updated_at
    profile.update_display_name(DisplayName("Bob"))
    assert profile.display_name.value == "Bob"
    assert profile.updated_at >= before

    profile.update_bio(None)
    assert profile.bio is None
    profile.update_avatar_url(" https://cdn.example/a.png ")
    assert profile.avatar_url == "https://cdn.example/a.png"
