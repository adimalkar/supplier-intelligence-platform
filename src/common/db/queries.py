"""
SIE Analytics — Shared Database Query Helpers.

Pre-built queries that multiple agents need. Import from here:

    from src.common.db.queries import get_supplier, get_recent_production_runs

All functions accept a SQLAlchemy Session as the first argument.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from src.common.db.models import (
    DimDefectType,
    DimEquipment,
    DimProductLine,
    DimSupplier,
    FactEquipmentEvent,
    FactProductionRun,
    FactQualityInspection,
)

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIMENSION QUERIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def get_supplier(session: Session, supplier_code: str) -> DimSupplier | None:
    """Get a supplier by code. Returns None if not found."""
    return session.execute(
        select(DimSupplier).where(DimSupplier.supplier_code == supplier_code)
    ).scalar_one_or_none()


def get_all_suppliers(session: Session) -> list[DimSupplier]:
    """Get all registered suppliers."""
    return list(session.execute(select(DimSupplier).order_by(DimSupplier.name)).scalars().all())


def get_supplier_by_id(session: Session, supplier_id: int) -> DimSupplier | None:
    """Get a supplier by ID."""
    return session.get(DimSupplier, supplier_id)


def get_equipment_for_supplier(session: Session, supplier_code: str) -> list[DimEquipment]:
    """Get all equipment belonging to a supplier."""
    return list(
        session.execute(
            select(DimEquipment)
            .join(DimProductLine)
            .join(DimSupplier)
            .where(DimSupplier.supplier_code == supplier_code)
            .order_by(DimEquipment.equipment_code)
        )
        .scalars()
        .all()
    )


def get_product_lines_for_supplier(session: Session, supplier_code: str) -> list[DimProductLine]:
    """Get all product lines belonging to a supplier."""
    return list(
        session.execute(
            select(DimProductLine)
            .join(DimSupplier)
            .where(DimSupplier.supplier_code == supplier_code)
            .order_by(DimProductLine.line_code)
        )
        .scalars()
        .all()
    )


def get_equipment_by_code(session: Session, equipment_code: str) -> DimEquipment | None:
    """Get equipment by its unique code."""
    return session.execute(
        select(DimEquipment).where(DimEquipment.equipment_code == equipment_code)
    ).scalar_one_or_none()


def get_all_defect_types(session: Session) -> list[DimDefectType]:
    """Get all defect type definitions."""
    return list(session.execute(select(DimDefectType).order_by(DimDefectType.code)).scalars().all())


def resolve_supplier_id(session: Session, supplier_code: str) -> int | None:
    """Resolve a supplier_code to supplier_id. Returns None if not found."""
    result = session.execute(
        select(DimSupplier.supplier_id).where(DimSupplier.supplier_code == supplier_code)
    ).scalar_one_or_none()
    return result


def resolve_equipment_id(session: Session, equipment_code: str) -> int | None:
    """Resolve an equipment_code to equipment_id. Returns None if not found."""
    result = session.execute(
        select(DimEquipment.equipment_id).where(DimEquipment.equipment_code == equipment_code)
    ).scalar_one_or_none()
    return result


def resolve_product_line_id(session: Session, supplier_code: str, line_code: str) -> int | None:
    """Resolve supplier_code + line_code to product_line_id."""
    result = session.execute(
        select(DimProductLine.product_line_id)
        .join(DimSupplier)
        .where(DimSupplier.supplier_code == supplier_code, DimProductLine.line_code == line_code)
    ).scalar_one_or_none()
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACT TABLE QUERIES (Read)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def get_recent_production_runs(
    session: Session, supplier_code: str, hours: int = 1
) -> list[FactProductionRun]:
    """Get production runs for a supplier in the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return list(
        session.execute(
            select(FactProductionRun)
            .join(DimSupplier)
            .where(
                DimSupplier.supplier_code == supplier_code,
                FactProductionRun.timestamp >= cutoff,
            )
            .order_by(FactProductionRun.timestamp.desc())
        )
        .scalars()
        .all()
    )


def get_recent_equipment_events(
    session: Session, equipment_code: str, hours: int = 1
) -> list[FactEquipmentEvent]:
    """Get equipment events for a specific equipment in the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return list(
        session.execute(
            select(FactEquipmentEvent)
            .join(DimEquipment)
            .where(
                DimEquipment.equipment_code == equipment_code,
                FactEquipmentEvent.timestamp >= cutoff,
            )
            .order_by(FactEquipmentEvent.timestamp.desc())
        )
        .scalars()
        .all()
    )


def get_recent_inspections(
    session: Session, supplier_code: str, hours: int = 1
) -> list[FactQualityInspection]:
    """Get quality inspections for a supplier in the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return list(
        session.execute(
            select(FactQualityInspection)
            .join(DimSupplier, FactQualityInspection.supplier_id == DimSupplier.supplier_id)
            .where(
                DimSupplier.supplier_code == supplier_code,
                FactQualityInspection.timestamp >= cutoff,
            )
            .order_by(FactQualityInspection.timestamp.desc())
        )
        .scalars()
        .all()
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KPI QUERIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def get_supplier_kpis(session: Session, supplier_code: str, target_date: date | None = None) -> dict[str, Any]:
    """
    Get KPI summary for a supplier on a given date.

    Returns:
        {
            "supplier_code": str,
            "avg_oee": float | None,
            "avg_yield": float | None,
            "total_units_produced": int,
            "total_units_passed": int,
            "total_runs": int,
            "defect_count": int,
            "avg_cycle_time": float | None,
        }
    """
    if target_date is None:
        target_date = date.today()

    day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    prod_stats = session.execute(
        select(
            func.avg(FactProductionRun.oee).label("avg_oee"),
            func.avg(FactProductionRun.yield_rate).label("avg_yield"),
            func.sum(FactProductionRun.units_produced).label("total_produced"),
            func.sum(FactProductionRun.units_passed).label("total_passed"),
            func.count(FactProductionRun.run_id).label("total_runs"),
            func.avg(FactProductionRun.cycle_time_seconds).label("avg_cycle_time"),
        )
        .join(DimSupplier)
        .where(
            DimSupplier.supplier_code == supplier_code,
            FactProductionRun.timestamp >= day_start,
            FactProductionRun.timestamp < day_end,
        )
    ).one()

    defect_count = session.execute(
        select(func.count(FactQualityInspection.inspection_id))
        .join(DimSupplier, FactQualityInspection.supplier_id == DimSupplier.supplier_id)
        .where(
            DimSupplier.supplier_code == supplier_code,
            FactQualityInspection.result == "fail",
            FactQualityInspection.timestamp >= day_start,
            FactQualityInspection.timestamp < day_end,
        )
    ).scalar() or 0

    return {
        "supplier_code": supplier_code,
        "avg_oee": float(prod_stats.avg_oee) if prod_stats.avg_oee else None,
        "avg_yield": float(prod_stats.avg_yield) if prod_stats.avg_yield else None,
        "total_units_produced": int(prod_stats.total_produced or 0),
        "total_units_passed": int(prod_stats.total_passed or 0),
        "total_runs": int(prod_stats.total_runs or 0),
        "defect_count": defect_count,
        "avg_cycle_time": float(prod_stats.avg_cycle_time) if prod_stats.avg_cycle_time else None,
    }


def get_all_supplier_kpis(session: Session, target_date: date | None = None) -> list[dict[str, Any]]:
    """Get KPI summaries for all suppliers."""
    suppliers = get_all_suppliers(session)
    return [get_supplier_kpis(session, s.supplier_code, target_date) for s in suppliers]


def get_defect_summary(
    session: Session, supplier_code: str, days: int = 7
) -> list[dict[str, Any]]:
    """
    Get defect summary grouped by defect type for the last N days.

    Returns list of dicts with: defect_code, defect_name, severity, count
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    results = session.execute(
        select(
            DimDefectType.code,
            DimDefectType.name,
            DimDefectType.severity,
            func.count(FactQualityInspection.inspection_id).label("count"),
        )
        .join(DimDefectType, FactQualityInspection.defect_type_id == DimDefectType.defect_type_id)
        .join(DimSupplier, FactQualityInspection.supplier_id == DimSupplier.supplier_id)
        .where(
            DimSupplier.supplier_code == supplier_code,
            FactQualityInspection.result == "fail",
            FactQualityInspection.timestamp >= cutoff,
        )
        .group_by(DimDefectType.code, DimDefectType.name, DimDefectType.severity)
        .order_by(func.count(FactQualityInspection.inspection_id).desc())
    ).all()

    return [
        {"defect_code": r.code, "defect_name": r.name, "severity": r.severity, "count": r.count}
        for r in results
    ]


def get_alert_history(
    session: Session, supplier_code: str | None = None, hours: int = 24
) -> list[dict[str, Any]]:
    """
    Get recent alerts from the materialized view or fact tables.

    Note: This queries quality inspections with 'fail' results as a proxy
    for alerts. The Orchestrator may enhance this with a dedicated alerts table.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    query = (
        select(
            FactQualityInspection.inspection_id,
            DimSupplier.supplier_code,
            FactQualityInspection.timestamp,
            FactQualityInspection.inspection_type,
            FactQualityInspection.result,
            FactQualityInspection.confidence,
            DimDefectType.name.label("defect_name"),
            DimDefectType.severity,
        )
        .join(DimSupplier, FactQualityInspection.supplier_id == DimSupplier.supplier_id)
        .outerjoin(
            DimDefectType,
            FactQualityInspection.defect_type_id == DimDefectType.defect_type_id,
        )
        .where(
            FactQualityInspection.result == "fail",
            FactQualityInspection.timestamp >= cutoff,
        )
        .order_by(FactQualityInspection.timestamp.desc())
    )

    if supplier_code:
        query = query.where(DimSupplier.supplier_code == supplier_code)

    results = session.execute(query).all()

    return [
        {
            "inspection_id": r.inspection_id,
            "supplier_code": r.supplier_code,
            "timestamp": r.timestamp.isoformat(),
            "inspection_type": r.inspection_type,
            "result": r.result,
            "confidence": r.confidence,
            "defect_name": r.defect_name,
            "severity": r.severity,
        }
        for r in results
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BULK INSERT HELPERS (for Pipeline Agent)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def insert_production_runs_bulk(session: Session, records: list[dict[str, Any]]) -> int:
    """
    Bulk insert production run records.

    Args:
        records: List of dicts matching FactProductionRun columns.

    Returns:
        Number of records inserted.
    """
    if not records:
        return 0
    session.execute(FactProductionRun.__table__.insert(), records)
    session.flush()
    logger.info("Inserted %d production runs", len(records))
    return len(records)


def insert_equipment_events_bulk(session: Session, records: list[dict[str, Any]]) -> int:
    """Bulk insert equipment event records."""
    if not records:
        return 0
    session.execute(FactEquipmentEvent.__table__.insert(), records)
    session.flush()
    logger.info("Inserted %d equipment events", len(records))
    return len(records)


def insert_quality_inspections_bulk(session: Session, records: list[dict[str, Any]]) -> int:
    """Bulk insert quality inspection records."""
    if not records:
        return 0
    session.execute(FactQualityInspection.__table__.insert(), records)
    session.flush()
    logger.info("Inserted %d quality inspections", len(records))
    return len(records)


def insert_alert(session: Session, alert_data: dict[str, Any]) -> int:
    """
    Insert an alert as a quality inspection record with result='fail'.

    Returns the inspection_id.
    """
    inspection = FactQualityInspection(**alert_data)
    session.add(inspection)
    session.flush()
    return inspection.inspection_id
