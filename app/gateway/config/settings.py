from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
_ENV_FILE_ARG = _ENV_FILE if _ENV_FILE.is_file() else None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GATEWAY_",
        env_file=_ENV_FILE_ARG,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "OpenChat Gateway"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Upstream services (edge routing only — no business DB here).
    auth_service_url: str = "http://localhost:8001"

    # JWT verify only — public key must match auth's signing key pair.
    jwt_algorithm: str = "RS256"
    jwt_public_key: str = ""
    jwt_public_key_path: str = ""

    # Outbound HTTP client.
    http_timeout_seconds: float = 30.0


settings = Settings()
