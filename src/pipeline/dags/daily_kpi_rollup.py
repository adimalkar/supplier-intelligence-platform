from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.pipeline.transforms.kpi import calculate_cpk

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def refresh_materialized_views(**context):
    from src.common.db.connection import SessionLocal
    from sqlalchemy import text
    with SessionLocal() as session:
        session.execute(text("REFRESH MATERIALIZED VIEW mv_hourly_supplier_kpis"))
        session.execute(text("REFRESH MATERIALIZED VIEW mv_daily_defect_summary"))
        session.execute(text("REFRESH MATERIALIZED VIEW mv_equipment_health_latest"))
        session.commit()
    print("Refreshed materialized views in TimescaleDB.")

def calc_cpk_and_slas(**context):
    from src.common.db.connection import SessionLocal
    from src.common.db.queries import get_all_suppliers, get_recent_production_runs
    
    with SessionLocal() as session:
        suppliers = get_all_suppliers(session)
        for supplier in suppliers:
            runs = get_recent_production_runs(session, supplier.supplier_code, hours=24)
            if len(runs) > 1:
                # Calculate CPK on cycle time (example specs)
                data = [r.cycle_time_seconds for r in runs]
                # Fallback specs
                usl = 15.0
                lsl = 5.0
                cpk = calculate_cpk(data, usl, lsl)
                print(f"Supplier {supplier.supplier_code} CPK: {cpk:.2f}")
                if cpk < 1.0:
                    print(f"SLA Warning: Supplier {supplier.supplier_code} CPK below 1.0")

def generate_report(**context):
    print("Daily report generated.")

with DAG(
    'daily_kpi_rollup',
    default_args=default_args,
    description='Daily KPI calculation and reporting',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['pipeline', 'kpi'],
) as dag:

    refresh_views = PythonOperator(
        task_id='refresh_materialized_views',
        python_callable=refresh_materialized_views,
    )
    
    calculate_kpis = PythonOperator(
        task_id='calc_cpk_and_slas',
        python_callable=calc_cpk_and_slas,
    )
    
    report = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
    )
    
    refresh_views >> calculate_kpis >> report
