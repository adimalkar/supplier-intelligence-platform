"""
SIE Analytics — Kafka Topic Constants.

Single source of truth for topic names. All agents import from here:

    from src.common.kafka.topics import Topics

    producer.produce(Topics.TELEMETRY_RAW, ...)
"""

from __future__ import annotations


class Topics:
    """Kafka topic name constants — never hardcode topic strings."""

    # Raw data from ingestion API
    TELEMETRY_RAW: str = "supplier.telemetry.raw"
    IMAGES_RAW: str = "supplier.images.raw"

    # Processed/transformed data
    TELEMETRY_TRANSFORMED: str = "supplier.telemetry.transformed"

    # Alerts and notifications
    ALERTS: str = "supplier.alerts"

    # Schema management
    SCHEMA_CHANGES: str = "supplier.schema-changes"

    @classmethod
    def all_topics(cls) -> list[str]:
        """Return all topic names for setup/validation."""
        return [
            cls.TELEMETRY_RAW,
            cls.IMAGES_RAW,
            cls.TELEMETRY_TRANSFORMED,
            cls.ALERTS,
            cls.SCHEMA_CHANGES,
        ]

    @classmethod
    def topic_configs(cls) -> dict[str, dict]:
        """
        Return topic configurations for creation.

        Keys are topic names, values have 'num_partitions' and 'replication_factor'.
        """
        return {
            cls.TELEMETRY_RAW: {"num_partitions": 5, "replication_factor": 1},
            cls.IMAGES_RAW: {"num_partitions": 3, "replication_factor": 1},
            cls.TELEMETRY_TRANSFORMED: {"num_partitions": 5, "replication_factor": 1},
            cls.ALERTS: {"num_partitions": 3, "replication_factor": 1},
            cls.SCHEMA_CHANGES: {"num_partitions": 1, "replication_factor": 1},
        }
