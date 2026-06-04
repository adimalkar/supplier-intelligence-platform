"""
SIE Analytics — SQLAlchemy 2.0 ORM Models.

This is the single source of truth for the database schema.
All agents must import models from here:

    from src.common.db.models import (
        DimSupplier, DimProductLine, DimEquipment, DimDefectType,
        FactProductionRun, FactQualityInspection, FactEquipmentEvent,
    )

Star Schema Design:
    Dimensions: suppliers, product_lines, equipment, defect_types
    Facts: production_runs, quality_inspections, equipment_events
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIMENSION TABLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class DimSupplier(Base):
    """Supplier dimension — represents a manufacturing supplier."""

    __tablename__ = "dim_suppliers"

    supplier_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    tier: Mapped[str] = mapped_column(String(20), nullable=False)  # "tier_1", "tier_2", "tier_3"
    contact_info: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    product_lines: Mapped[list[DimProductLine]] = relationship(back_populates="supplier")
    production_runs: Mapped[list[FactProductionRun]] = relationship(back_populates="supplier")
    equipment_events: Mapped[list[FactEquipmentEvent]] = relationship(back_populates="supplier")

    def __repr__(self) -> str:
        return f"<DimSupplier(code={self.supplier_code!r}, name={self.name!r})>"


class DimProductLine(Base):
    """Product line dimension — a production line belonging to a supplier."""

    __tablename__ = "dim_product_lines"
    __table_args__ = (
        UniqueConstraint("supplier_id", "line_code", name="uq_supplier_line"),
    )

    product_line_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_suppliers.supplier_id"), nullable=False
    )
    line_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_type: Mapped[str] = mapped_column(String(100), nullable=False)
    specifications: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    supplier: Mapped[DimSupplier] = relationship(back_populates="product_lines")
    equipment: Mapped[list[DimEquipment]] = relationship(back_populates="product_line")
    production_runs: Mapped[list[FactProductionRun]] = relationship(back_populates="product_line")

    def __repr__(self) -> str:
        return f"<DimProductLine(code={self.line_code!r}, name={self.name!r})>"


class DimEquipment(Base):
    """Equipment dimension — a piece of manufacturing equipment on a production line."""

    __tablename__ = "dim_equipment"

    equipment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_line_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_product_lines.product_line_id"), nullable=False
    )
    equipment_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    equipment_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "smt_machine", "aoi", "reflow_oven", etc.
    manufacturer: Mapped[str] = mapped_column(String(200), nullable=False)
    install_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    maintenance_schedule: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    product_line: Mapped[DimProductLine] = relationship(back_populates="equipment")
    production_runs: Mapped[list[FactProductionRun]] = relationship(back_populates="equipment")
    equipment_events: Mapped[list[FactEquipmentEvent]] = relationship(back_populates="equipment")

    def __repr__(self) -> str:
        return f"<DimEquipment(code={self.equipment_code!r}, type={self.equipment_type!r})>"


class DimDefectType(Base):
    """Defect type dimension — classification of manufacturing defects."""

    __tablename__ = "dim_defect_types"

    defect_type_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "critical", "major", "minor"
    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "visual", "dimensional", "electrical", "mechanical"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    quality_inspections: Mapped[list[FactQualityInspection]] = relationship(
        back_populates="defect_type"
    )

    def __repr__(self) -> str:
        return f"<DimDefectType(code={self.code!r}, severity={self.severity!r})>"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACT TABLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class FactProductionRun(Base):
    """Fact table — individual production run records from suppliers."""

    __tablename__ = "fact_production_runs"
    __table_args__ = (
        Index("ix_prod_runs_supplier_ts", "supplier_id", "timestamp"),
        Index("ix_prod_runs_timestamp", "timestamp"),
    )

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_suppliers.supplier_id"), nullable=False
    )
    product_line_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_product_lines.product_line_id"), nullable=False
    )
    equipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_equipment.equipment_id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    cycle_time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    units_produced: Mapped[int] = mapped_column(Integer, nullable=False)
    units_passed: Mapped[int] = mapped_column(Integer, nullable=False)
    yield_rate: Mapped[float] = mapped_column(Float, nullable=False)  # units_passed / units_produced
    oee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    process_params: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    supplier: Mapped[DimSupplier] = relationship(back_populates="production_runs")
    product_line: Mapped[DimProductLine] = relationship(back_populates="production_runs")
    equipment: Mapped[DimEquipment] = relationship(back_populates="production_runs")
    quality_inspections: Mapped[list[FactQualityInspection]] = relationship(
        back_populates="production_run"
    )

    def __repr__(self) -> str:
        return (
            f"<FactProductionRun(id={self.run_id}, supplier={self.supplier_id}, "
            f"yield={self.yield_rate:.2%})>"
        )


class FactQualityInspection(Base):
    """Fact table — quality inspection results (manual + CV-based)."""

    __tablename__ = "fact_quality_inspections"
    __table_args__ = (
        Index("ix_quality_supplier_ts", "supplier_id", "timestamp"),
        Index("ix_quality_timestamp", "timestamp"),
    )

    inspection_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("fact_production_runs.run_id"), nullable=True
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_suppliers.supplier_id"), nullable=False
    )
    defect_type_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("dim_defect_types.defect_type_id"), nullable=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    inspection_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "visual", "xray", "thermal", "cv_automated"
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # "pass", "fail", "warning"
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # CV confidence score
    bbox_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # bounding box data
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    production_run: Mapped[Optional[FactProductionRun]] = relationship(
        back_populates="quality_inspections"
    )
    defect_type: Mapped[Optional[DimDefectType]] = relationship(
        back_populates="quality_inspections"
    )

    def __repr__(self) -> str:
        return (
            f"<FactQualityInspection(id={self.inspection_id}, result={self.result!r}, "
            f"confidence={self.confidence})>"
        )


class FactEquipmentEvent(Base):
    """Fact table — equipment telemetry and status events."""

    __tablename__ = "fact_equipment_events"
    __table_args__ = (
        Index("ix_equip_events_equipment_ts", "equipment_id", "timestamp"),
        Index("ix_equip_events_timestamp", "timestamp"),
    )

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_equipment.equipment_id"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_suppliers.supplier_id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "telemetry", "maintenance", "fault", "startup", "shutdown"
    temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pressure_psi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vibration_mm_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    power_consumption_kw: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="running"
    )  # "running", "idle", "maintenance", "fault"

    # Relationships
    equipment: Mapped[DimEquipment] = relationship(back_populates="equipment_events")
    supplier: Mapped[DimSupplier] = relationship(back_populates="equipment_events")

    def __repr__(self) -> str:
        return (
            f"<FactEquipmentEvent(id={self.event_id}, type={self.event_type!r}, "
            f"status={self.status!r})>"
        )
