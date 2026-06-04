"""
SIE Analytics — Kafka Serializers & Deserializers.

Standard JSON serialization for all Kafka messages. All agents use these:

    from src.common.kafka.serializers import serialize_json, deserialize_json
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def serialize_json(data: dict[str, Any]) -> bytes:
    """
    Serialize a dict to JSON bytes for Kafka.

    Handles datetime serialization and adds metadata.
    """
    def _default(obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    return json.dumps(data, default=_default).encode("utf-8")


def deserialize_json(data: bytes) -> dict[str, Any]:
    """
    Deserialize JSON bytes from Kafka to a dict.

    Returns empty dict on failure (logs error).
    """
    try:
        return json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error("Failed to deserialize Kafka message: %s", e)
        return {}


def make_event_id() -> str:
    """Generate a unique event ID for Kafka messages."""
    return str(uuid.uuid4())


def make_timestamp() -> str:
    """Generate an ISO-8601 UTC timestamp for Kafka messages."""
    return datetime.now(timezone.utc).isoformat()


def wrap_telemetry_event(
    supplier_code: str,
    equipment_code: str,
    product_line_code: str,
    timestamp: str,
    cycle_time_seconds: float,
    units_produced: int,
    units_passed: int,
    temperature_c: float,
    pressure_psi: float,
    vibration_mm_s: float,
    power_consumption_kw: float,
    process_params: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Create a standardized TelemetryPayload dict for Kafka.

    This is the contract schema for supplier.telemetry.raw topic.
    """
    return {
        "event_id": make_event_id(),
        "supplier_code": supplier_code,
        "equipment_code": equipment_code,
        "product_line_code": product_line_code,
        "timestamp": timestamp,
        "cycle_time_seconds": cycle_time_seconds,
        "units_produced": units_produced,
        "units_passed": units_passed,
        "temperature_c": temperature_c,
        "pressure_psi": pressure_psi,
        "vibration_mm_s": vibration_mm_s,
        "power_consumption_kw": power_consumption_kw,
        "process_params": process_params or {},
        "ingested_at": make_timestamp(),
    }


def wrap_image_event(
    supplier_code: str,
    equipment_code: str,
    timestamp: str,
    image_path: str,
    image_format: str = "jpeg",
    inspection_type: str = "visual",
) -> dict[str, Any]:
    """
    Create a standardized ImagePayload dict for Kafka.

    This is the contract schema for supplier.images.raw topic.
    """
    return {
        "image_id": make_event_id(),
        "supplier_code": supplier_code,
        "equipment_code": equipment_code,
        "timestamp": timestamp,
        "image_path": image_path,
        "image_format": image_format,
        "inspection_type": inspection_type,
        "ingested_at": make_timestamp(),
    }


def wrap_alert_event(
    supplier_code: str,
    severity: str,
    alert_type: str,
    title: str,
    description: str,
    metric_name: str = "",
    metric_value: float = 0.0,
    threshold: float = 0.0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a standardized AlertPayload dict for Kafka.

    This is the contract schema for supplier.alerts topic.

    Args:
        severity: "critical", "warning", or "info"
        alert_type: "yield_drop", "equipment_fault", "quality_fail", "defect_detected"
    """
    return {
        "alert_id": make_event_id(),
        "supplier_code": supplier_code,
        "severity": severity,
        "alert_type": alert_type,
        "title": title,
        "description": description,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "threshold": threshold,
        "timestamp": make_timestamp(),
        "metadata": metadata or {},
    }
