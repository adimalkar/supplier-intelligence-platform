"""
SIE Analytics — Kafka Connection Configuration.

All agents use this for Kafka producer/consumer setup:

    from src.common.kafka.config import get_producer_config, get_consumer_config

Usage:
    producer = Producer(get_producer_config())
    consumer = Consumer(get_consumer_config("ingest-transform"))
"""

from __future__ import annotations

import logging

from src.common.config import settings

logger = logging.getLogger(__name__)


def get_producer_config(client_id: str = "sie-producer") -> dict:
    """
    Get Kafka producer configuration dict.

    Compatible with confluent_kafka.Producer().

    Args:
        client_id: Unique identifier for this producer instance.
    """
    return {
        "bootstrap.servers": settings.kafka.BOOTSTRAP_SERVERS,
        "security.protocol": settings.kafka.SECURITY_PROTOCOL,
        "client.id": client_id,
        "acks": "all",
        "linger.ms": 50,  # Batch for 50ms before sending
        "batch.size": 65536,  # 64KB batch size
        "compression.type": "lz4",
        "retries": 3,
        "retry.backoff.ms": 100,
    }


def get_consumer_config(group_suffix: str, auto_commit: bool = False) -> dict:
    """
    Get Kafka consumer configuration dict.

    Compatible with confluent_kafka.Consumer().

    Args:
        group_suffix: Appended to the consumer group prefix to form the group ID.
                      Example: "ingest-transform" → "sie-ingest-transform"
        auto_commit: Whether to auto-commit offsets. Default False for manual control.
    """
    group_id = f"{settings.kafka.CONSUMER_GROUP_PREFIX}-{group_suffix}"
    return {
        "bootstrap.servers": settings.kafka.BOOTSTRAP_SERVERS,
        "security.protocol": settings.kafka.SECURITY_PROTOCOL,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": auto_commit,
        "max.poll.interval.ms": 300000,  # 5 minutes
        "session.timeout.ms": 30000,
        "fetch.min.bytes": 1024,
        "fetch.wait.max.ms": 500,
    }


def check_kafka_health() -> dict:
    """
    Check Kafka connectivity and return status.

    Returns:
        dict with keys: "status" ("healthy" | "unhealthy"), "details"
    """
    try:
        from confluent_kafka.admin import AdminClient

        admin = AdminClient({"bootstrap.servers": settings.kafka.BOOTSTRAP_SERVERS})
        metadata = admin.list_topics(timeout=10)

        return {
            "status": "healthy",
            "details": {
                "bootstrap_servers": settings.kafka.BOOTSTRAP_SERVERS,
                "broker_count": len(metadata.brokers),
                "topic_count": len(metadata.topics),
                "topics": list(metadata.topics.keys()),
            },
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "details": {"error": str(e)},
        }
