"""
SIE Analytics — Pydantic Models (API Contracts).

These are the shared data contracts that define the shape of all data
flowing through the system. Agents import from here:

    from src.ingestion_api.models.telemetry import TelemetryBatchRequest
    from src.ingestion_api.models.supplier import SupplierCreate, SupplierResponse

These models are used by:
- Agent 2 (Ingestion API) for request/response validation
- Agent 3 (Pipeline) for data transformation type safety
- Agent 6 (Dashboard) for query result typing
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TELEMETRY MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TelemetryRecord(BaseModel):
    """A single telemetry data point from a supplier."""

    supplier_code: str = Field(..., min_length=1, max_length=50, description="Unique supplier identifier")
    equipment_code: str = Field(..., min_length=1, max_length=50, description="Equipment identifier")
    product_line_code: str = Field(..., min_length=1, max_length=50, description="Product line identifier")
    timestamp: datetime = Field(..., description="Event timestamp (ISO-8601)")
    cycle_time_seconds: float = Field(..., gt=0, le=600, description="Cycle time in seconds")
    units_produced: int = Field(..., ge=0, description="Units produced in this cycle")
    units_passed: int = Field(..., ge=0, description="Units that passed QA")
    temperature_c: float = Field(default=0.0, ge=-50, le=500, description="Equipment temperature °C")
    pressure_psi: float = Field(default=0.0, ge=0, le=1000, description="Operating pressure PSI")
    vibration_mm_s: float = Field(default=0.0, ge=0, le=100, description="Vibration mm/s")
    power_consumption_kw: float = Field(default=0.0, ge=0, le=1000, description="Power consumption kW")
    process_params: dict[str, str] = Field(default_factory=dict, description="Additional process parameters")

    @field_validator("units_passed")
    @classmethod
    def units_passed_lte_produced(cls, v: int, info: Any) -> int:
        """Ensure units_passed does not exceed units_produced."""
        if "units_produced" in info.data and v > info.data["units_produced"]:
            raise ValueError("units_passed cannot exceed units_produced")
        return v


class TelemetryBatchRequest(BaseModel):
    """Batch telemetry ingestion request."""

    records: list[TelemetryRecord] = Field(..., min_length=1, max_length=1000)


class TelemetryBatchResponse(BaseModel):
    """Response from batch telemetry ingestion."""

    accepted: int = Field(..., description="Number of records accepted")
    rejected: int = Field(default=0, description="Number of records rejected")
    errors: list[str] = Field(default_factory=list, description="Validation error messages")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUPPLIER MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class SupplierCreate(BaseModel):
    """Request body for creating a new supplier."""

    supplier_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    tier: str = Field(..., pattern=r"^tier_[1-3]$")
    contact_info: dict[str, str] = Field(default_factory=dict)


class SupplierUpdate(BaseModel):
    """Request body for updating a supplier."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    tier: Optional[str] = Field(None, pattern=r"^tier_[1-3]$")
    contact_info: Optional[dict[str, str]] = None


class SupplierResponse(BaseModel):
    """Supplier data returned in API responses."""

    supplier_id: int
    supplier_code: str
    name: str
    location: str
    tier: str
    contact_info: dict[str, str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierKPIResponse(BaseModel):
    """Supplier KPI summary returned by the API."""

    supplier_code: str
    avg_oee: Optional[float] = None
    avg_yield: Optional[float] = None
    total_units_produced: int = 0
    total_units_passed: int = 0
    total_runs: int = 0
    defect_count: int = 0
    avg_cycle_time: Optional[float] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCHEMA VALIDATION MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class FieldDefinition(BaseModel):
    """Definition of a single field in a supplier schema."""

    name: str = Field(..., min_length=1)
    type: str = Field(..., description="Data type: string, integer, float, boolean, datetime, json")
    required: bool = Field(default=True)
    description: str = Field(default="")
    constraints: dict[str, Any] = Field(default_factory=dict, description="E.g., min, max, pattern")


class SchemaValidationRequest(BaseModel):
    """Request to validate a proposed supplier data schema."""

    supplier_code: str
    schema_version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    fields: list[FieldDefinition] = Field(..., min_length=1)


class SchemaCompatibilityResult(BaseModel):
    """Result of schema compatibility check."""

    is_compatible: bool
    added_fields: list[str] = Field(default_factory=list)
    removed_fields: list[str] = Field(default_factory=list)
    type_changes: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IMAGE / CV MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class InspectionImageMeta(BaseModel):
    """Metadata for an inspection image (passed through Kafka)."""

    image_id: str
    supplier_code: str
    equipment_code: str
    timestamp: datetime
    image_path: str
    image_format: str = "jpeg"
    inspection_type: str = "visual"  # "visual", "xray", "thermal"


class DetectionResult(BaseModel):
    """Result from the CV defect detection model."""

    class_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)


class InspectionResult(BaseModel):
    """Full inspection result combining image metadata + detections."""

    image_id: str
    supplier_code: str
    equipment_code: str
    timestamp: datetime
    detections: list[DetectionResult]
    overall_result: str  # "pass" or "fail"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ALERT MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class AlertEvent(BaseModel):
    """An alert event (consumed from Kafka, displayed in dashboard)."""

    alert_id: str
    supplier_code: str
    severity: str = Field(..., pattern=r"^(critical|warning|info)$")
    alert_type: str  # "yield_drop", "equipment_fault", "quality_fail", "defect_detected"
    title: str
    description: str
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENT AI MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class AgentQuery(BaseModel):
    """Request to the Agentic AI module."""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Response from the Agentic AI module."""

    text: str
    data: Optional[dict[str, Any]] = None
    visualization_type: Optional[str] = None  # "table", "line_chart", "bar_chart"
    sources: list[str] = Field(default_factory=list)
