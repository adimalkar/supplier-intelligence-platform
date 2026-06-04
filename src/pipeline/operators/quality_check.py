from typing import Any, Dict
import json
import pandas as pd
import great_expectations as ge
from airflow.models import BaseOperator
from airflow.exceptions import AirflowFailException

class GreatExpectationsOperator(BaseOperator):
    """Run a Great Expectations suite against a list of records passed via XCom."""
    
    def __init__(
        self,
        *,
        suite_path: str,
        data_task_id: str,
        fail_on_error: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.suite_path = suite_path
        self.data_task_id = data_task_id
        self.fail_on_error = fail_on_error

    def execute(self, context: Any) -> Dict[str, Any]:
        data = context['ti'].xcom_pull(task_ids=self.data_task_id)
        if not data:
            self.log.info("No data to validate.")
            return {"success": True, "statistics": {}}
            
        df = pd.DataFrame(data)
        
        # Using from_pandas which is simpler for operators without full GE context
        ge_df = ge.from_pandas(df)
        
        with open(self.suite_path, 'r') as f:
            suite_dict = json.load(f)
            
        # Add expectations
        for exp in suite_dict.get('expectations', []):
            kwargs = exp.get('kwargs', {})
            expectation_type = exp.get('expectation_type')
            
            # Use getattr to call the expectation method dynamically
            if hasattr(ge_df, expectation_type):
                method = getattr(ge_df, expectation_type)
                method(**kwargs)
            else:
                self.log.warning(f"Expectation {expectation_type} not found on GE DataFrame.")
                
        results = ge_df.validate()
        
        success = results.get("success", False)
        stats = results.get("statistics", {})
        
        if not success and self.fail_on_error:
            raise AirflowFailException(f"Great Expectations validation failed: {stats}")
            
        self.log.info(f"Validation success: {success}, stats: {stats}")
        return {"success": success, "statistics": stats}
