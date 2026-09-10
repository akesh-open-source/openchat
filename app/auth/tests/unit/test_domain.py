from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.auth.domain.entities.device import Device
from app.auth.domain.entities.refresh_token import RefreshToken, new_refresh_family_id
from app.auth.domain.entities.session import Session
from app.auth.domain.entities.user import User
from app.auth.domain.exceptions import (
    InvalidDisplayNameError,
    InvalidEmailError,
    InvalidPasswordError,
)
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password


def test_email_normalizes_and_validates() -> None:
    email = Email("  User@Example.COM ")
    assert email.value == "user@example.com"
    assert str(email) == "user@example.com"


@pytest.mark.parametrize("value", ["", "not-an-email", "a@", "@b.com"])
def test_email_rejects_invalid(value: str) -> None:
    with pytest.raises(InvalidEmailError):
        Email(value)


def test_password_validate_plain() -> None:
    Password.validate_plain("longenough")
    with pytest.raises(InvalidPasswordError):
        Password.validate_plain("short")
    with pytest.raises(InvalidPasswordError):
        Password.validate_plain("")
    with pytest.raises(InvalidPasswordError):
        Password("")


def test_display_name_bounds() -> None:
    assert DisplayName("  Alice  ").value == "Alice"
    with pytest.raises(InvalidDisplayNameError):
        DisplayName("ab")
    with pytest.raises(InvalidDisplayNameError):
        DisplayName("x" * 31)


def test_user_create_and_update_password() -> None:
    user = User.create(
        Email("user@example.com"),
        DisplayName("Alice"),
        Password("hashed-password"),
    )
    assert user.is_active is True
    user.update_password(Password("new-hash"))
    assert user.password.hashed_value == "new-hash"
    user.deactivate()
    assert user.is_active is False


def test_session_active_and_revoke() -> None:
    session = Session.create(
        user_id=uuid4(),
        device_id=uuid4(),
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    assert session.is_active is True
    session.revoke()
    assert session.is_revoked is True
    assert session.is_active is False


def test_device_create_and_touch() -> None:
    user_id = uuid4()
    device = Device.create(
        user_id=user_id,
        client_device_id="  phone-1  ",
        name="  iPhone  ",
    )
    assert device.client_device_id == "phone-1"
    assert device.name == "iPhone"
    device.touch(name="iPhone 15", user_agent="OpenChat/1.0")
    assert device.name == "iPhone 15"
    assert device.user_agent == "OpenChat/1.0"


def test_refresh_token_revoke() -> None:
    token = RefreshToken.create(
        token_id=uuid4(),
        user_id=uuid4(),
        token_hash="abc",
        family_id=new_refresh_family_id(),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        session_id=uuid4(),
    )
    replacement = uuid4()
    token.revoke(replaced_by_id=replacement)
    assert token.is_revoked is True
    assert token.replaced_by_id == replacement
