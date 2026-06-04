# API Reference

## REST API (FastAPI)

The Ingestion API exposes REST endpoints for traditional HTTP ingestion.

### `POST /api/v1/telemetry`
**Headers**: `X-API-Key: string`
**Body**:
```json
{
  "supplier_code": "SUP-001",
  "equipment_code": "EQ-001",
  "temperature": 65.5,
  "pressure": 120.0,
  "vibration": 2.1,
  "status": "running"
}
```

### `GET /health`
Returns the health status of the API.

## gRPC API

The system uses gRPC for high-throughput edge telemetry.
Service: `TelemetryIngestion`
RPCs:
- `StreamTelemetry (stream TelemetryBatch) returns (IngestionResponse)`
- `StreamImages (stream ImageBatch) returns (IngestionResponse)`
