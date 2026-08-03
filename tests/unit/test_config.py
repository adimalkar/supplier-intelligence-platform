"""
Unit tests for global configuration settings and environment variable overrides.
"""

import pytest
from pydantic_settings import BaseSettings

from src.common.config import (
    DatabaseSettings,
    KafkaSettings,
    APISettings,
    SimulatorSettings,
    CVSettings,
    AISettings,
    DashboardSettings,
    Settings,
    get_settings,
)


def test_database_settings_urls():
    """Verify correct assembly of sync and async PostgreSQL SQLAlchemy connection strings."""
    db = DatabaseSettings(
        HOST="test_db",
        PORT=5433,
        NAME="test_database",
        USER="admin",
        PASSWORD="secret_password",
    )
    assert db.url == "postgresql://admin:secret_password@test_db:5433/test_database"
    assert db.async_url == "postgresql+asyncpg://admin:secret_password@test_db:5433/test_database"


def test_env_prefix_override(monkeypatch: pytest.MonkeyPatch):
    """Ensure environment variable prefixes correctly override default setting values."""
    monkeypatch.setenv("DB_HOST", "prod-rds-instance.aws.com")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("API_PORT", "8080")
    monkeypatch.setenv("DASHBOARD_THEME", "light")

    # Instantiate directly to pick up new environment variables without hitting cache
    db = DatabaseSettings()
    api = APISettings()
    dashboard = DashboardSettings()

    assert db.HOST == "prod-rds-instance.aws.com"
    assert db.PORT == 5432
    assert api.PORT == 8080
    assert dashboard.THEME == "light"


def test_settings_aggregation():
    """Test root Settings class aggregates all submodule defaults seamlessly."""
    root = Settings()
    assert isinstance(root.db, DatabaseSettings)
    assert isinstance(root.kafka, KafkaSettings)
    assert isinstance(root.api, APISettings)
    assert isinstance(root.simulator, SimulatorSettings)
    assert isinstance(root.cv, CVSettings)
    assert isinstance(root.ai, AISettings)
    assert isinstance(root.dashboard, DashboardSettings)
    assert root.LOG_FORMAT == "json"


def test_get_settings_caching():
    """Confirm lru_cache returns identical instances across successive invocations."""
    instance_one = get_settings()
    instance_two = get_settings()
    assert instance_one is instance_two
