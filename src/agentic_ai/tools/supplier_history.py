import json
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from datetime import date, timedelta
from src.common.db.queries import get_supplier_kpis

class SupplierHistoryInput(BaseModel):
    supplier_code: str = Field(description="The unique code of the supplier (e.g. 'SUP-001').")
    metric: str = Field(description="The metric to retrieve (e.g. 'oee', 'yield').")
    days: int = Field(default=7, description="Number of past days to retrieve data for.")

class SupplierHistoryTool(BaseTool):
    name: str = "supplier_history"
    description: str = "Retrieves trend data and statistical summary for a specific supplier and metric over time."
    args_schema: Type[BaseModel] = SupplierHistoryInput
    session_factory: Any = None

    def __init__(self, session_factory: Any, **kwargs):
        super().__init__(**kwargs)
        self.session_factory = session_factory

    def _run(self, supplier_code: str, metric: str, days: int = 7, run_manager: Optional[Any] = None) -> str:
        try:
            with self.session_factory() as session:
                end_date = date.today()
                start_date = end_date - timedelta(days=days)
                
                history = []
                for i in range(days + 1):
                    current_date = start_date + timedelta(days=i)
                    # Use get_supplier_kpis if it returns a dictionary of metrics
                    try:
                        kpis = get_supplier_kpis(session, supplier_code, current_date)
                    except Exception:
                        kpis = {} # mock behavior if not implemented
                        
                    if kpis and metric in kpis:
                        history.append({
                            "date": current_date.isoformat(),
                            "metric": metric,
                            "value": kpis[metric]
                        })
                
                if not history:
                    return f"No data found for supplier {supplier_code} and metric {metric} in the last {days} days."
                
                values = [item["value"] for item in history if isinstance(item["value"], (int, float))]
                
                summary = {}
                if values:
                    summary = {
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "trend": "up" if values[-1] >= values[0] else "down"
                    }
                
                return json.dumps({"history": history, "summary": summary}, indent=2)
        except Exception as e:
            return f"Error retrieving supplier history: {str(e)}"

    async def _arun(self, supplier_code: str, metric: str, days: int = 7, run_manager: Optional[Any] = None) -> str:
        return self._run(supplier_code, metric, days, run_manager)
