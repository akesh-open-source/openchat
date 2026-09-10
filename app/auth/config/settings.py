from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
_ENV_FILE_ARG = _ENV_FILE if _ENV_FILE.is_file() else None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=_ENV_FILE_ARG,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "OpenChat Auth Service"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/openchat_auth"
    )

    # Shared engine pool — caps open DB connections under load.
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # JWT — RS256: auth signs with private key; verifiers use public key only.
    jwt_algorithm: str = "RS256"
    jwt_private_key: str = ""
    jwt_private_key_path: str = ""
    jwt_public_key: str = ""
    jwt_public_key_path: str = ""
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    password_reset_token_expire_minutes: int = 30
    registration_token_expire_minutes: int = 60

    # Redis (pending registration tokens, etc.)
    redis_url: str = "redis://localhost:6379/0"

    # SMTP email delivery (use Mailpit locally: host=mailpit, port=1025).
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = False
    smtp_use_ssl: bool = False
    smtp_from_email: str = "noreply@openchat.local"
    smtp_from_name: str = "OpenChat"
    # Link bases used in transactional emails (frontend or docs URL).
    password_reset_url_base: str = "http://localhost:8000/docs"
    registration_verify_url_base: str = "http://localhost:8000/docs"
    login_url: str = "http://localhost:8000/docs"

    # Rate limits (fixed window per client IP).
    rate_limit_window_seconds: int = 60
    rate_limit_login_per_window: int = 10
    rate_limit_register_per_window: int = 5
    rate_limit_password_reset_per_window: int = 5
    rate_limit_refresh_per_window: int = 30
    rate_limit_default_per_window: int = 60


settings = Settings()
