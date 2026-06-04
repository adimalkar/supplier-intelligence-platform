from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.pipeline.transforms.anomaly import detect_z_score_anomaly
from src.common.kafka.topics import Topics

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def monitor_kpis(**context):
    from src.common.db.connection import SessionLocal
    from src.common.db.queries import get_all_suppliers, get_recent_production_runs, insert_alert
    
    with SessionLocal() as session:
        suppliers = get_all_suppliers(session)
        for supplier in suppliers:
            # Fetch recent runs
            runs = get_recent_production_runs(session, supplier.supplier_code, hours=24)
            if len(runs) < 5:
                continue
            
            # Extract yield history, newest first, so we reverse it
            yields = [r.yield_rate for r in reversed(runs)]
            current = yields[-1]
            history = yields[:-1]
            
            if history and detect_z_score_anomaly(current, history, threshold=3.0):
                print(f"Anomaly detected for {supplier.supplier_code}! Current: {current:.2f}, History mean: {sum(history)/len(history):.2f}")
                # Insert alert to DB
                alert_data = {
                    "supplier_id": supplier.supplier_id,
                    "defect_type_id": None,
                    "timestamp": datetime.now(),
                    "inspection_type": "anomaly_detection",
                    "result": "fail",
                    "confidence": 1.0,
                    "bbox_metadata": {"metric": "yield_rate", "value": current, "history_mean": sum(history)/len(history)},
                    "image_path": ""
                }
                insert_alert(session, alert_data)
                session.commit()
                print(f"Alert published for {supplier.supplier_code}")

with DAG(
    'alerting',
    default_args=default_args,
    description='Monitor KPIs and publish alerts',
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['pipeline', 'alerts'],
) as dag:

    monitor = PythonOperator(
        task_id='monitor_kpis',
        python_callable=monitor_kpis,
    )
