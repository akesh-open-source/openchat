from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoginUserCommand:
    email: str
    password: str
