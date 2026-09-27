from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Tawassl Security Studio"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Security controls
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    LOCAL_API_SECRET: str = "tawassl-local-secret-change-in-production"
    CSRF_HEADER_NAME: str = "X-Tawassl-CSRF"

    # Storage paths
    DATA_DIR: Path = Path("./data")
    DATABASE_PATH: Path = Path("./data/tawassl.db")
    SANDBOX_DIR: Path = Path("./data/sandbox")

    # AI configuration
    DEFAULT_AI_PROVIDER: str = "mock"  # "mock" | "gemini" | "openai"
    DEFAULT_MODEL_ID: str = "mock-sec-v1"
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # Hard execution limits & budgets
    DEFAULT_MAX_STEPS: int = 20
    DEFAULT_MAX_REQUESTS: int = 50
    DEFAULT_MAX_TOOL_CALLS: int = 30
    DEFAULT_TIMEOUT_SECONDS: int = 300
    DEFAULT_MAX_OUTPUT_BYTES: int = 2 * 1024 * 1024  # 2MB

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]


settings = Settings()
