from datetime import datetime, timedelta
import random
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from src.pipeline.operators.quality_check import GreatExpectationsOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_recent_data(**context) -> list[dict]:
    from src.common.db.connection import SessionLocal
    from sqlalchemy import text
    
    with SessionLocal() as session:
        # Fetch actual recent runs for validation
        result = session.execute(text(
            "SELECT s.supplier_code, r.yield_rate, r.units_produced, r.cycle_time_seconds "
            "FROM fact_production_runs r "
            "JOIN dim_suppliers s ON r.supplier_id = s.supplier_id "
            "ORDER BY r.timestamp DESC LIMIT 100"
        )).fetchall()
        
        return [
            {"supplier_code": r.supplier_code, "yield_rate": r.yield_rate, "units_produced": r.units_produced, "cycle_time_seconds": r.cycle_time_seconds}
            for r in result
        ]

def branch_on_quality(**context) -> str:
    validation_res = context['ti'].xcom_pull(task_ids='run_ge_suite')
    if validation_res and validation_res.get('success'):
        return 'log_success'
    return 'alert_failure'

with DAG(
    'quality_validation',
    default_args=default_args,
    description='Validate data quality with Great Expectations',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['pipeline', 'quality'],
) as dag:

    fetch_data = PythonOperator(
        task_id='fetch_recent_data',
        python_callable=fetch_recent_data,
    )

    run_ge_suite = GreatExpectationsOperator(
        task_id='run_ge_suite',
        data_task_id='fetch_recent_data',
        suite_path='src/pipeline/expectations/supplier_telemetry_suite.json',
        fail_on_error=False,
    )

    branch = BranchPythonOperator(
        task_id='branch_on_quality',
        python_callable=branch_on_quality,
    )

    log_success = EmptyOperator(task_id='log_success')
    alert_failure = EmptyOperator(task_id='alert_failure')

    fetch_data >> run_ge_suite >> branch
    branch >> log_success
    branch >> alert_failure
