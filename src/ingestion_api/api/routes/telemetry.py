from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.ingestion_api.models.contracts import TelemetryBatchRequest, TelemetryBatchResponse
from src.ingestion_api.kafka_producer.producer import producer
from src.common.kafka.serializers import wrap_telemetry_event
from src.common.db.connection import get_session
from src.common.kafka.topics import Topics
from src.common.db.queries import get_recent_production_runs

router = APIRouter()

@router.post("/batch", response_model=TelemetryBatchResponse)
def ingest_telemetry_batch(request: TelemetryBatchRequest):
    accepted = 0
    errors = []
    
    for record in request.records:
        try:
            payload = wrap_telemetry_event(
                supplier_code=record.supplier_code,
                equipment_code=record.equipment_code,
                product_line_code=record.product_line_code,
                timestamp=record.timestamp.isoformat(),
                cycle_time_seconds=record.cycle_time_seconds,
                units_produced=record.units_produced,
                units_passed=record.units_passed,
                temperature_c=record.temperature_c,
                pressure_psi=record.pressure_psi,
                vibration_mm_s=record.vibration_mm_s,
                power_consumption_kw=record.power_consumption_kw,
                process_params=record.process_params
            )
            
            producer.produce_message(
                topic=Topics.TELEMETRY_RAW,
                key=record.supplier_code,
                value=payload
            )
            accepted += 1
        except Exception as e:
            errors.append(str(e))
            
    producer.flush()
    return TelemetryBatchResponse(
        accepted=accepted,
        rejected=len(request.records) - accepted,
        errors=errors
    )

@router.get("/latest/{supplier_code}")
def get_latest_telemetry(supplier_code: str, db: Session = Depends(get_session)):
    runs = get_recent_production_runs(db, supplier_code, hours=1)
    
    return [
        {
            "run_id": str(r.run_id),
            "timestamp": r.timestamp,
            "cycle_time_seconds": float(r.cycle_time_seconds),
            "units_produced": int(r.units_produced),
            "units_passed": int(r.units_passed),
            "oee": float(r.oee) if r.oee else None,
        }
        for r in runs[:50]
    ]
