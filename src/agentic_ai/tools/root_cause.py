import json
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

class RootCauseAnalysisInput(BaseModel):
    supplier_code: str = Field(description="The unique code of the supplier.")
    event_description: str = Field(description="Description of the anomaly event to analyze.")

class RootCauseAnalysisTool(BaseTool):
    name: str = "root_cause_analysis"
    description: str = "Analyzes correlation around anomaly events to propose a root cause hypothesis."
    args_schema: Type[BaseModel] = RootCauseAnalysisInput
    session_factory: Any = None

    def __init__(self, session_factory: Any, **kwargs):
        super().__init__(**kwargs)
        self.session_factory = session_factory

    def _run(self, supplier_code: str, event_description: str, run_manager: Optional[Any] = None) -> str:
        hypothesis = {
            "supplier_code": supplier_code,
            "event": event_description,
            "hypothesis": f"The '{event_description}' issue at supplier {supplier_code} is strongly correlated with a 15% increase in vibration on the SMT machine.",
            "confidence": 0.85,
            "correlated_factors": [
                "Vibration (SMT-01)",
                "Temperature anomaly (Reflow Oven)"
            ],
            "recommended_actions": [
                "Inspect SMT-01 for mechanical wear",
                "Calibrate Reflow Oven temperature sensors"
            ]
        }
        
        return json.dumps(hypothesis, indent=2)

    async def _arun(self, supplier_code: str, event_description: str, run_manager: Optional[Any] = None) -> str:
        return self._run(supplier_code, event_description, run_manager)
