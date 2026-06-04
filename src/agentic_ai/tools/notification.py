import json
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

class NotificationDrafterInput(BaseModel):
    supplier_code: str = Field(description="The unique code of the supplier.")
    issue_description: str = Field(description="Description of the issue to notify the supplier about.")
    suggested_actions: str = Field(default="Please investigate.", description="Suggested corrective actions.")

class NotificationDrafterTool(BaseTool):
    name: str = "notification_drafter"
    description: str = "Generates a corrective action email draft to send to a supplier."
    args_schema: Type[BaseModel] = NotificationDrafterInput

    def _run(self, supplier_code: str, issue_description: str, suggested_actions: str = "Please investigate.", run_manager: Optional[Any] = None) -> str:
        email_draft = {
            "subject": f"URGENT: Corrective Action Required for {supplier_code} - {issue_description}",
            "body": f"Dear Supplier {supplier_code} Team,\n\n"
                    f"We have detected an anomaly regarding: {issue_description}.\n\n"
                    f"Based on our analysis, we recommend the following corrective actions:\n"
                    f"{suggested_actions}\n\n"
                    f"Please investigate and respond with your action plan within 24 hours.\n\n"
                    f"Best regards,\n"
                    f"Supplier Intelligence Platform",
            "to": f"quality@{supplier_code.lower()}.com"
        }
        return json.dumps(email_draft, indent=2)

    async def _arun(self, supplier_code: str, issue_description: str, suggested_actions: str = "Please investigate.", run_manager: Optional[Any] = None) -> str:
        return self._run(supplier_code, issue_description, suggested_actions, run_manager)
