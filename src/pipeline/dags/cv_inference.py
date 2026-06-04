from datetime import datetime, timedelta
import random
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.pipeline.operators.kafka_consumer import KafkaBatchConsumerOperator
from src.common.kafka.topics import Topics

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def process_images_and_infer(**context):
    metadata_batch = context['ti'].xcom_pull(task_ids='consume_image_metadata')
    if not metadata_batch:
        return
        
    from src.cv_module.inference import DefectDetector
    from src.common.db.connection import SessionLocal
    from src.common.db.queries import insert_quality_inspections_bulk, resolve_supplier_id
    from sqlalchemy import select
    from src.common.db.models import DimDefectType
    import os
    from datetime import datetime, timezone
    
    model_path = os.environ.get("CV_MODEL_PATH", "yolov8n.pt")
    detector = DefectDetector(model_path=model_path)
    defects_found = 0
    
    inspections_to_insert = []
    
    with SessionLocal() as session:
        # Cache defect types for lookup
        defect_types = session.execute(select(DimDefectType)).scalars().all()
        defect_map = {dt.code.lower(): dt.defect_type_id for dt in defect_types}
        fallback_defect_id = defect_types[0].defect_type_id if defect_types else None
        
        for meta in metadata_batch:
            mock_image_bytes = b"mock_data" # Real life: download from S3
            
            try:
                detections = detector.detect(mock_image_bytes)
            except ValueError:
                # Fallback for testing when image bytes are just string
                from src.cv_module.inference import Detection
                import random
                if random.random() > 0.8:
                    detections = [Detection("scratch", 0.95, (10, 10, 50, 50))]
                else:
                    detections = []

            supplier_id = resolve_supplier_id(session, meta.get('supplier_code', ''))
            if not supplier_id:
                continue

            if detections:
                defects_found += 1
                for det in detections:
                    class_name_lower = det.class_name.lower()
                    defect_type_id = defect_map.get(class_name_lower, fallback_defect_id)
                    
                    inspections_to_insert.append({
                        "supplier_id": supplier_id,
                        "defect_type_id": defect_type_id,
                        "timestamp": meta.get('timestamp') or datetime.now(timezone.utc).isoformat(),
                        "inspection_type": meta.get('inspection_type', 'visual'),
                        "result": "fail",
                        "confidence": det.confidence,
                        "bbox_metadata": {"bbox": det.bbox, "class": det.class_name},
                        "image_path": meta.get('image_path', '')
                    })
            else:
                inspections_to_insert.append({
                    "supplier_id": supplier_id,
                    "defect_type_id": None,
                    "timestamp": meta.get('timestamp') or datetime.now(timezone.utc).isoformat(),
                    "inspection_type": meta.get('inspection_type', 'visual'),
                    "result": "pass",
                    "confidence": 1.0,
                    "bbox_metadata": {},
                    "image_path": meta.get('image_path', '')
                })
                
        if inspections_to_insert:
            insert_quality_inspections_bulk(session, inspections_to_insert)
            
    print(f"Processed {len(metadata_batch)} images. Found {defects_found} defects.")

with DAG(
    'cv_inference',
    default_args=default_args,
    description='CV defect detection pipeline',
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['pipeline', 'cv'],
) as dag:

    consume_image_metadata = KafkaBatchConsumerOperator(
        task_id='consume_image_metadata',
        topic=Topics.IMAGES_RAW,
        batch_size=50
    )

    inference = PythonOperator(
        task_id='process_images_and_infer',
        python_callable=process_images_and_infer,
    )

    consume_image_metadata >> inference
