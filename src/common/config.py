"""
Supplier Intelligence Platform — Global Configuration.

All services load their config from environment variables through this module.
Agents should import settings from here rather than reading env vars directly.

Usage:
    from src.common.config import settings
    print(settings.DB_HOST)
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL + TimescaleDB connection settings."""

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    HOST: str = "localhost"
    PORT: int = 5432
    NAME: str = "sie_analytics"
    USER: str = "sie_admin"
    PASSWORD: str = "sie_secure_password_change_me"
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20

    @property
    def url(self) -> str:
        """SQLAlchemy connection URL."""
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def async_url(self) -> str:
        """Async SQLAlchemy connection URL."""
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class KafkaSettings(BaseSettings):
    """Apache Kafka connection settings."""

    model_config = SettingsConfigDict(env_prefix="KAFKA_", env_file=".env", extra="ignore")

    BOOTSTRAP_SERVERS: str = "localhost:9092"
    SECURITY_PROTOCOL: str = "PLAINTEXT"
    CONSUMER_GROUP_PREFIX: str = "sie"


class APISettings(BaseSettings):
    """FastAPI Ingestion API settings."""

    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    GRPC_PORT: int = 50051
    KEY: str = "sie-api-key-change-me"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:8501", "http://localhost:3000"]


class SimulatorSettings(BaseSettings):
    """Edge Simulator settings."""

    model_config = SettingsConfigDict(env_prefix="SIMULATOR_", env_file=".env", extra="ignore")

    GRPC_TARGET: str = "localhost:50051"
    SPEED: float = 1.0
    ANOMALY_RATE: float = 0.05


class CVSettings(BaseSettings):
    """Computer Vision module settings."""

    model_config = SettingsConfigDict(env_prefix="CV_", env_file=".env", extra="ignore")

    MODEL_PATH: str = "src/cv_module/models/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    IMAGE_STORAGE_PATH: str = "./data/inspection_images"


class AISettings(BaseSettings):
    """Agentic AI module settings."""

    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    AWS_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"


class DashboardSettings(BaseSettings):
    """Streamlit Dashboard settings."""

    model_config = SettingsConfigDict(env_prefix="DASHBOARD_", env_file=".env", extra="ignore")

    DB_QUERY_CACHE_TTL: int = 30
    AUTO_REFRESH_SECONDS: int = 30
    THEME: str = "dark"


class Settings(BaseSettings):
    """Root settings — aggregates all sub-settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    db: DatabaseSettings = DatabaseSettings()
    kafka: KafkaSettings = KafkaSettings()
    api: APISettings = APISettings()
    simulator: SimulatorSettings = SimulatorSettings()
    cv: CVSettings = CVSettings()
    ai: AISettings = AISettings()
    dashboard: DashboardSettings = DashboardSettings()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance. Call this instead of instantiating directly."""
    return Settings()


# Convenience alias — most agents will just do: from src.common.config import settings
settings = get_settings()
