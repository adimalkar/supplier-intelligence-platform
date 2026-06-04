"""001 — Initial star schema: dimension and fact tables.

Revision ID: 001_initial_schema
Revises: None
Create Date: 2025-01-01 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Dimension: Suppliers ──
    op.create_table(
        "dim_suppliers",
        sa.Column("supplier_id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("supplier_code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("tier", sa.String(20), nullable=False),
        sa.Column("contact_info", sa.JSON(), default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_dim_suppliers_code", "dim_suppliers", ["supplier_code"])

    # ── Dimension: Product Lines ──
    op.create_table(
        "dim_product_lines",
        sa.Column("product_line_id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("dim_suppliers.supplier_id"), nullable=False),
        sa.Column("line_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("product_type", sa.String(100), nullable=False),
        sa.Column("specifications", sa.JSON(), default={}),
        sa.UniqueConstraint("supplier_id", "line_code", name="uq_supplier_line"),
    )
    op.create_index("ix_dim_product_lines_code", "dim_product_lines", ["line_code"])

    # ── Dimension: Equipment ──
    op.create_table(
        "dim_equipment",
        sa.Column("equipment_id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("product_line_id", sa.Integer(), sa.ForeignKey("dim_product_lines.product_line_id"), nullable=False),
        sa.Column("equipment_code", sa.String(50), nullable=False, unique=True),
        sa.Column("equipment_type", sa.String(100), nullable=False),
        sa.Column("manufacturer", sa.String(200), nullable=False),
        sa.Column("install_date", sa.Date(), nullable=True),
        sa.Column("maintenance_schedule", sa.JSON(), default={}),
    )
    op.create_index("ix_dim_equipment_code", "dim_equipment", ["equipment_code"])

    # ── Dimension: Defect Types ──
    op.create_table(
        "dim_defect_types",
        sa.Column("defect_type_id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_dim_defect_types_code", "dim_defect_types", ["code"])

    # ── Fact: Production Runs ──
    op.create_table(
        "fact_production_runs",
        sa.Column("run_id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("dim_suppliers.supplier_id"), nullable=False),
        sa.Column("product_line_id", sa.Integer(), sa.ForeignKey("dim_product_lines.product_line_id"), nullable=False),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("dim_equipment.equipment_id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cycle_time_seconds", sa.Float(), nullable=False),
        sa.Column("units_produced", sa.Integer(), nullable=False),
        sa.Column("units_passed", sa.Integer(), nullable=False),
        sa.Column("yield_rate", sa.Float(), nullable=False),
        sa.Column("oee", sa.Float(), nullable=True),
        sa.Column("process_params", sa.JSON(), default={}),
    )
    op.create_index("ix_prod_runs_timestamp", "fact_production_runs", ["timestamp"])
    op.create_index("ix_prod_runs_supplier_ts", "fact_production_runs", ["supplier_id", "timestamp"])

    # ── Fact: Quality Inspections ──
    op.create_table(
        "fact_quality_inspections",
        sa.Column("inspection_id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("fact_production_runs.run_id"), nullable=True),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("dim_suppliers.supplier_id"), nullable=False),
        sa.Column("defect_type_id", sa.Integer(), sa.ForeignKey("dim_defect_types.defect_type_id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inspection_type", sa.String(50), nullable=False),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("bbox_metadata", sa.JSON(), nullable=True),
        sa.Column("image_path", sa.String(500), nullable=True),
    )
    op.create_index("ix_quality_timestamp", "fact_quality_inspections", ["timestamp"])
    op.create_index("ix_quality_supplier_ts", "fact_quality_inspections", ["supplier_id", "timestamp"])

    # ── Fact: Equipment Events ──
    op.create_table(
        "fact_equipment_events",
        sa.Column("event_id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("dim_equipment.equipment_id"), nullable=False),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("dim_suppliers.supplier_id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("temperature_c", sa.Float(), nullable=True),
        sa.Column("pressure_psi", sa.Float(), nullable=True),
        sa.Column("vibration_mm_s", sa.Float(), nullable=True),
        sa.Column("power_consumption_kw", sa.Float(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="running"),
    )
    op.create_index("ix_equip_events_timestamp", "fact_equipment_events", ["timestamp"])
    op.create_index("ix_equip_events_equipment_ts", "fact_equipment_events", ["equipment_id", "timestamp"])


def downgrade() -> None:
    op.drop_table("fact_equipment_events")
    op.drop_table("fact_quality_inspections")
    op.drop_table("fact_production_runs")
    op.drop_table("dim_defect_types")
    op.drop_table("dim_equipment")
    op.drop_table("dim_product_lines")
    op.drop_table("dim_suppliers")
