from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InitiateRegisterCommand:
    email: str
    password: str
    display_name: str
