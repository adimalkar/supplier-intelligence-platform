"""
Pydantic contract models — re-export everything for clean imports.

Agents can import as:
    from src.ingestion_api.models import TelemetryRecord, SupplierCreate, AlertEvent
"""

from src.ingestion_api.models.contracts import (  # noqa: F401
    AgentQuery,
    AgentResponse,
    AlertEvent,
    DetectionResult,
    FieldDefinition,
    InspectionImageMeta,
    InspectionResult,
    SchemaCompatibilityResult,
    SchemaValidationRequest,
    SupplierCreate,
    SupplierKPIResponse,
    SupplierResponse,
    SupplierUpdate,
    TelemetryBatchRequest,
    TelemetryBatchResponse,
    TelemetryRecord,
)

__all__ = [
    "AgentQuery",
    "AgentResponse",
    "AlertEvent",
    "DetectionResult",
    "FieldDefinition",
    "InspectionImageMeta",
    "InspectionResult",
    "SchemaCompatibilityResult",
    "SchemaValidationRequest",
    "SupplierCreate",
    "SupplierKPIResponse",
    "SupplierResponse",
    "SupplierUpdate",
    "TelemetryBatchRequest",
    "TelemetryBatchResponse",
    "TelemetryRecord",
]
