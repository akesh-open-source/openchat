from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResetPasswordCommand:
    token: str
    new_password: str
