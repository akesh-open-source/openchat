# app/auth/application/commands/register_user.py
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: str
    password: str
    display_name: str