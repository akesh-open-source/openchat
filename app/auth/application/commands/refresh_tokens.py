from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RefreshTokensCommand:
    refresh_token: str
