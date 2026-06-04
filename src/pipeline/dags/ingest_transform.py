from datetime import datetime, timedelta
import json
from typing import Any
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.pipeline.operators.kafka_consumer import KafkaBatchConsumerOperator
from src.pipeline.transforms.telemetry import clean_telemetry
from src.common.kafka.topics import Topics
# Assume common modules can be imported once orchestrator starts
# We use mock DB insertion / publishing since Airflow connections require it
# For tests, these will just pass

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def transform_telemetry_func(**context: Any) -> list[dict]:
    # Extract messages from previous task
    messages = context['ti'].xcom_pull(task_ids='consume_telemetry')
    if not messages:
        return []
    
    transformed = []
    for msg in messages:
        cleaned = clean_telemetry(msg)
        
        # Calculate yield
        units_produced = cleaned.get('units_produced', 0)
        units_passed = cleaned.get('units_passed', 0)
        yield_rate = units_passed / units_produced if units_produced > 0 else 0.0
        cleaned['yield_rate'] = yield_rate
        
        # Dummy OEE (needs availability and performance, which might come from state)
        # Using a simplistic calculation for demonstration
        cleaned['oee'] = yield_rate * 0.9 * 0.95 
        
        cleaned['transformed_at'] = datetime.utcnow().isoformat()
        transformed.append(cleaned)
        
    return transformed

def load_to_db_and_publish(**context: Any) -> None:
    transformed = context['ti'].xcom_pull(task_ids='transform_telemetry')
    if not transformed:
        return
        
    # In a real pipeline, we'd use src.common.db.connection and src.common.db.queries.insert_production_runs_bulk
    # and confluent_kafka to publish to Topics.TELEMETRY_TRANSFORMED
    # We leave this as a stub for the DAG definition
    print(f"Loaded {len(transformed)} records to DB and published to Kafka.")

with DAG(
    'ingest_transform',
    default_args=default_args,
    description='Consume telemetry from Kafka, transform, and load',
    schedule_interval=timedelta(minutes=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['pipeline', 'telemetry'],
) as dag:

    consume_telemetry = KafkaBatchConsumerOperator(
        task_id='consume_telemetry',
        topic=Topics.TELEMETRY_RAW,
        batch_size=1000
    )

    transform_telemetry = PythonOperator(
        task_id='transform_telemetry',
        python_callable=transform_telemetry_func,
    )
    
    load_and_publish = PythonOperator(
        task_id='load_to_db_and_publish',
        python_callable=load_to_db_and_publish,
    )

    consume_telemetry >> transform_telemetry >> load_and_publish
