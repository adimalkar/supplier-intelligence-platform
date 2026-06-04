"""002 — Convert fact tables to TimescaleDB hypertables.

Revision ID: 002_timescaledb_hypertables
Revises: 001_initial_schema
Create Date: 2025-01-01 00:01:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "002_timescaledb_hypertables"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

    # Convert fact tables to hypertables (partitioned by timestamp)
    # chunk_time_interval = 1 day
    op.execute(
        "SELECT create_hypertable('fact_production_runs', 'timestamp', "
        "chunk_time_interval => INTERVAL '1 day', "
        "migrate_data => true, "
        "if_not_exists => true);"
    )
    op.execute(
        "SELECT create_hypertable('fact_quality_inspections', 'timestamp', "
        "chunk_time_interval => INTERVAL '1 day', "
        "migrate_data => true, "
        "if_not_exists => true);"
    )
    op.execute(
        "SELECT create_hypertable('fact_equipment_events', 'timestamp', "
        "chunk_time_interval => INTERVAL '1 day', "
        "migrate_data => true, "
        "if_not_exists => true);"
    )

    # Add compression policies (compress chunks older than 7 days)
    op.execute(
        "ALTER TABLE fact_production_runs SET ("
        "timescaledb.compress, "
        "timescaledb.compress_segmentby = 'supplier_id', "
        "timescaledb.compress_orderby = 'timestamp DESC'"
        ");"
    )
    op.execute(
        "SELECT add_compression_policy('fact_production_runs', INTERVAL '7 days', if_not_exists => true);"
    )

    op.execute(
        "ALTER TABLE fact_quality_inspections SET ("
        "timescaledb.compress, "
        "timescaledb.compress_segmentby = 'supplier_id', "
        "timescaledb.compress_orderby = 'timestamp DESC'"
        ");"
    )
    op.execute(
        "SELECT add_compression_policy('fact_quality_inspections', INTERVAL '7 days', if_not_exists => true);"
    )

    op.execute(
        "ALTER TABLE fact_equipment_events SET ("
        "timescaledb.compress, "
        "timescaledb.compress_segmentby = 'equipment_id', "
        "timescaledb.compress_orderby = 'timestamp DESC'"
        ");"
    )
    op.execute(
        "SELECT add_compression_policy('fact_equipment_events', INTERVAL '7 days', if_not_exists => true);"
    )


def downgrade() -> None:
    # Remove compression policies
    op.execute("SELECT remove_compression_policy('fact_production_runs', if_exists => true);")
    op.execute("SELECT remove_compression_policy('fact_quality_inspections', if_exists => true);")
    op.execute("SELECT remove_compression_policy('fact_equipment_events', if_exists => true);")

    # Note: Cannot easily revert hypertable to regular table.
    # In practice, you would drop and recreate the tables.
    pass
