"""Application settings configuration.

This module defines the application's settings using Pydantic.
The settings can be configured via environment variables and
include configurations for logging, database connections, and OpenAI API.

Dependencies:
    - enum: For defining enumeration types.
    - pathlib: For handling filesystem paths.
    - tempfile: For accessing temporary directory paths.
    - pydantic_settings: For creating settings with validation.
    - yarl: For building URLs.

Classes:
    LogLevel: Enum representing possible log levels for the application.
    Settings: Pydantic class for application settings, including
              database and API configurations.
"""

import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str
    port: int
    # quantity of workers for uvicorn
    workers_count: int = 8
    # Enable uvicorn reloading
    reload: bool = False

    # OpenAI
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    token_cost: float = 0.002 / 1000000
    encoding_name: str = "cl100k_base"

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    # Variables for the database
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_base: str
    db_echo: bool = False

    # This variable is used to define
    # multiproc_dir. It's required for [uvi|guni]corn projects.
    prometheus_dir: Path = TEMP_DIR / "prom"

    @property
    def db_url(self) -> URL:
        """Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PORTFOLIO_BACKEND_",
        env_file_encoding="utf-8",
    )


settings = Settings()  # type: ignore
