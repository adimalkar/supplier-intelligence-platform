import pytest
from airflow.models import DagBag

def test_no_import_errors():
    dag_bag = DagBag(dag_folder='src/pipeline/dags/', include_examples=False)
    assert len(dag_bag.import_errors) == 0, f"DAG import errors: {dag_bag.import_errors}"

def test_expected_dags_loaded():
    dag_bag = DagBag(dag_folder='src/pipeline/dags/', include_examples=False)
    expected_dags = ['ingest_transform', 'quality_validation', 'daily_kpi_rollup', 'cv_inference', 'alerting']
    for dag_id in expected_dags:
        assert dag_id in dag_bag.dags, f"DAG {dag_id} not found in DagBag"
