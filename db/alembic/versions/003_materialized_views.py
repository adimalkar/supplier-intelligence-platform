"""003 — Create materialized views for dashboard queries.

Revision ID: 003_materialized_views
Revises: 002_timescaledb_hypertables
Create Date: 2025-01-01 00:02:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "003_materialized_views"
down_revision: Union[str, None] = "002_timescaledb_hypertables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Hourly Supplier KPIs ──
    # Pre-aggregated hourly metrics per supplier for fast dashboard queries
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hourly_supplier_kpis AS
        SELECT
            time_bucket('1 hour', pr.timestamp) AS hour,
            s.supplier_id,
            s.supplier_code,
            s.name AS supplier_name,
            AVG(pr.oee) AS avg_oee,
            AVG(pr.yield_rate) AS avg_yield,
            SUM(pr.units_produced) AS total_units_produced,
            SUM(pr.units_passed) AS total_units_passed,
            COUNT(pr.run_id) AS total_runs,
            AVG(pr.cycle_time_seconds) AS avg_cycle_time,
            MIN(pr.yield_rate) AS min_yield,
            MAX(pr.yield_rate) AS max_yield,
            STDDEV(pr.yield_rate) AS stddev_yield
        FROM fact_production_runs pr
        JOIN dim_suppliers s ON pr.supplier_id = s.supplier_id
        GROUP BY hour, s.supplier_id, s.supplier_code, s.name
        ORDER BY hour DESC;
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_mv_hourly_kpis_hour_supplier "
        "ON mv_hourly_supplier_kpis (hour, supplier_id);"
    )

    # ── Daily Defect Summary ──
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_defect_summary AS
        SELECT
            time_bucket('1 day', qi.timestamp) AS day,
            s.supplier_id,
            s.supplier_code,
            dt.defect_type_id,
            dt.code AS defect_code,
            dt.name AS defect_name,
            dt.severity,
            dt.category,
            COUNT(qi.inspection_id) AS defect_count,
            AVG(qi.confidence) AS avg_confidence
        FROM fact_quality_inspections qi
        JOIN dim_suppliers s ON qi.supplier_id = s.supplier_id
        LEFT JOIN dim_defect_types dt ON qi.defect_type_id = dt.defect_type_id
        WHERE qi.result = 'fail'
        GROUP BY day, s.supplier_id, s.supplier_code,
                 dt.defect_type_id, dt.code, dt.name, dt.severity, dt.category
        ORDER BY day DESC, defect_count DESC;
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_mv_daily_defects "
        "ON mv_daily_defect_summary (day, supplier_id, defect_type_id);"
    )

    # ── Latest Equipment Health Snapshot ──
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_equipment_health_latest AS
        SELECT DISTINCT ON (e.equipment_id)
            e.equipment_id,
            e.equipment_code,
            e.equipment_type,
            e.manufacturer,
            pl.line_code AS product_line_code,
            s.supplier_code,
            s.name AS supplier_name,
            ev.timestamp AS last_event_time,
            ev.event_type,
            ev.temperature_c,
            ev.pressure_psi,
            ev.vibration_mm_s,
            ev.power_consumption_kw,
            ev.status
        FROM dim_equipment e
        JOIN dim_product_lines pl ON e.product_line_id = pl.product_line_id
        JOIN dim_suppliers s ON pl.supplier_id = s.supplier_id
        LEFT JOIN fact_equipment_events ev ON e.equipment_id = ev.equipment_id
        ORDER BY e.equipment_id, ev.timestamp DESC NULLS LAST;
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_mv_equip_health "
        "ON mv_equipment_health_latest (equipment_id);"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_equipment_health_latest CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_daily_defect_summary CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_hourly_supplier_kpis CASCADE;")
