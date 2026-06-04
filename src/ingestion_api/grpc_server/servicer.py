import logging
import os
import uuid
from datetime import datetime, timezone

from src.ingestion_api.proto import telemetry_pb2, telemetry_pb2_grpc
from src.ingestion_api.kafka_producer.producer import producer
from src.common.kafka.serializers import wrap_telemetry_event, wrap_image_event
from src.common.kafka.topics import Topics

logger = logging.getLogger(__name__)

class TelemetryServicer(telemetry_pb2_grpc.TelemetryServiceServicer):
    def StreamTelemetry(self, request_iterator, context):
        count = 0
        try:
            for event in request_iterator:
                dt = datetime.fromtimestamp(event.timestamp_ms / 1000.0, tz=timezone.utc)
                payload = wrap_telemetry_event(
                    supplier_code=event.supplier_code,
                    equipment_code=event.equipment_code,
                    product_line_code=event.product_line_code,
                    timestamp=dt.isoformat(),
                    cycle_time_seconds=event.cycle_time_seconds,
                    units_produced=event.units_produced,
                    units_passed=event.units_passed,
                    temperature_c=event.temperature_c,
                    pressure_psi=event.pressure_psi,
                    vibration_mm_s=event.vibration_mm_s,
                    power_consumption_kw=event.power_consumption_kw,
                    process_params=dict(event.process_params)
                )
                
                producer.produce_message(
                    topic=Topics.TELEMETRY_RAW,
                    key=event.supplier_code,
                    value=payload
                )
                count += 1
            producer.flush()
            return telemetry_pb2.TelemetryAck(success=True, message=f"Processed {count} telemetry events")
        except Exception as e:
            logger.error(f"Error in StreamTelemetry: {e}")
            return telemetry_pb2.TelemetryAck(success=False, message=str(e))

    def StreamInspectionImage(self, request_iterator, context):
        count = 0
        try:
            for image_event in request_iterator:
                dt = datetime.fromtimestamp(image_event.timestamp_ms / 1000.0, tz=timezone.utc)
                
                os.makedirs("/tmp/sie_images", exist_ok=True)
                image_id = str(uuid.uuid4())
                ext = image_event.image_format or "jpeg"
                filepath = f"/tmp/sie_images/{image_id}.{ext}"
                with open(filepath, "wb") as f:
                    f.write(image_event.image_data)
                    
                payload = wrap_image_event(
                    supplier_code=image_event.supplier_code,
                    equipment_code=image_event.equipment_code,
                    timestamp=dt.isoformat(),
                    image_path=filepath,
                    image_format=image_event.image_format,
                    inspection_type=image_event.inspection_type
                )
                
                producer.produce_message(
                    topic=Topics.IMAGES_RAW,
                    key=image_event.supplier_code,
                    value=payload
                )
                count += 1
            producer.flush()
            return telemetry_pb2.InspectionAck(success=True, message=f"Processed {count} images")
        except Exception as e:
            logger.error(f"Error in StreamInspectionImage: {e}")
            return telemetry_pb2.InspectionAck(success=False, message=str(e))
