"""
SIE Analytics — Shared Test Fixtures.

Provides database sessions, test data factories, and common mocks
for all test suites. Import fixtures by adding this to conftest.py
in test subdirectories or directly use these.

Usage in tests:
    def test_something(db_session, sample_supplier):
        ...
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Set test env vars BEFORE importing app modules
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "sie_analytics_test")
os.environ.setdefault("DB_USER", "sie_admin")
os.environ.setdefault("DB_PASSWORD", "sie_secure_password_change_me")
os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")

from src.common.db.models import (  # noqa: E402
    Base,
    DimDefectType,
    DimEquipment,
    DimProductLine,
    DimSupplier,
    FactEquipmentEvent,
    FactProductionRun,
    FactQualityInspection,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE FIXTURES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}",
)


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine (session-scoped for performance)."""
    engine = create_engine(TEST_DB_URL, echo=False)
    # Create all tables (skip TimescaleDB-specific stuff for unit tests)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Provide a transactional test session that rolls back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, expire_on_commit=False)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST DATA FACTORIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@pytest.fixture
def sample_supplier(db_session: Session) -> DimSupplier:
    """Create and return a sample supplier for testing."""
    supplier = DimSupplier(
        supplier_code="TEST_SUPPLIER",
        name="Test Supplier Co.",
        location="Test City, TX, USA",
        tier="tier_1",
        contact_info={"primary": "test@test.com"},
    )
    db_session.add(supplier)
    db_session.flush()
    return supplier


@pytest.fixture
def sample_product_line(db_session: Session, sample_supplier: DimSupplier) -> DimProductLine:
    """Create and return a sample product line."""
    line = DimProductLine(
        supplier_id=sample_supplier.supplier_id,
        line_code="TEST_LINE_A",
        name="Test Assembly Line A",
        product_type="test_component",
        specifications={"capacity_per_hour": 100, "target_oee": 0.85},
    )
    db_session.add(line)
    db_session.flush()
    return line


@pytest.fixture
def sample_equipment(db_session: Session, sample_product_line: DimProductLine) -> DimEquipment:
    """Create and return a sample equipment unit."""
    equipment = DimEquipment(
        product_line_id=sample_product_line.product_line_id,
        equipment_code="TEST_SMT_01",
        equipment_type="smt_machine",
        manufacturer="Test Manufacturer",
        install_date=date(2023, 1, 1),
        maintenance_schedule={"preventive_interval_days": 30},
    )
    db_session.add(equipment)
    db_session.flush()
    return equipment


@pytest.fixture
def sample_defect_type(db_session: Session) -> DimDefectType:
    """Create and return a sample defect type."""
    defect = DimDefectType(
        code="TEST_SCRATCH",
        name="Test Scratch Defect",
        severity="minor",
        category="visual",
        description="A test scratch defect",
    )
    db_session.add(defect)
    db_session.flush()
    return defect


@pytest.fixture
def sample_production_run(
    db_session: Session,
    sample_supplier: DimSupplier,
    sample_product_line: DimProductLine,
    sample_equipment: DimEquipment,
) -> FactProductionRun:
    """Create and return a sample production run record."""
    run = FactProductionRun(
        supplier_id=sample_supplier.supplier_id,
        product_line_id=sample_product_line.product_line_id,
        equipment_id=sample_equipment.equipment_id,
        timestamp=datetime.now(timezone.utc),
        cycle_time_seconds=12.5,
        units_produced=100,
        units_passed=97,
        yield_rate=0.97,
        oee=0.85,
        process_params={"speed": "high", "temperature": "220"},
    )
    db_session.add(run)
    db_session.flush()
    return run


@pytest.fixture
def sample_equipment_event(
    db_session: Session,
    sample_supplier: DimSupplier,
    sample_equipment: DimEquipment,
) -> FactEquipmentEvent:
    """Create and return a sample equipment event."""
    event = FactEquipmentEvent(
        equipment_id=sample_equipment.equipment_id,
        supplier_id=sample_supplier.supplier_id,
        timestamp=datetime.now(timezone.utc),
        event_type="telemetry",
        temperature_c=65.3,
        pressure_psi=42.1,
        vibration_mm_s=2.8,
        power_consumption_kw=15.7,
        status="running",
    )
    db_session.add(event)
    db_session.flush()
    return event


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KAFKA MOCK FIXTURES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@pytest.fixture
def sample_telemetry_payload() -> dict:
    """A sample Kafka telemetry payload matching the contract schema."""
    return {
        "event_id": "test-event-001",
        "supplier_code": "TEST_SUPPLIER",
        "equipment_code": "TEST_SMT_01",
        "product_line_code": "TEST_LINE_A",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cycle_time_seconds": 12.5,
        "units_produced": 100,
        "units_passed": 97,
        "temperature_c": 65.3,
        "pressure_psi": 42.1,
        "vibration_mm_s": 2.8,
        "power_consumption_kw": 15.7,
        "process_params": {"speed": "high"},
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_alert_payload() -> dict:
    """A sample Kafka alert payload matching the contract schema."""
    return {
        "alert_id": "test-alert-001",
        "supplier_code": "TEST_SUPPLIER",
        "severity": "warning",
        "alert_type": "yield_drop",
        "title": "Yield Below Threshold",
        "description": "Supplier TEST_SUPPLIER yield dropped below 95%",
        "metric_name": "yield_rate",
        "metric_value": 0.92,
        "threshold": 0.95,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"production_line": "TEST_LINE_A"},
    }
