from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoginUserCommand:
    email: str
    password: str
    device_id: str
    device_name: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None
