from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
_ENV_FILE_ARG = _ENV_FILE if _ENV_FILE.is_file() else None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MESSAGING_",
        env_file=_ENV_FILE_ARG,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "OpenChat Messaging Service"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8003
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/openchat_messaging"
    )

    # Shared engine pool — caps open DB connections under load.
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800


settings = Settings()
