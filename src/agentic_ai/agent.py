from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import json
import logging

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import BedrockChat

from src.agentic_ai.tools.sql_query import SQLQueryTool
from src.agentic_ai.tools.supplier_history import SupplierHistoryTool
from src.agentic_ai.tools.root_cause import RootCauseAnalysisTool
from src.agentic_ai.tools.notification import NotificationDrafterTool
from src.agentic_ai.prompts.system import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    text: str
    data: dict | None
    visualization_type: str | None
    sources: list[str]

class SupplierIntelligenceAgent:
    def __init__(self, db_session_factory, llm_config: dict):
        self.db_session_factory = db_session_factory
        self.llm_config = llm_config
        
        self.tools = [
            SQLQueryTool(session_factory=self.db_session_factory),
            SupplierHistoryTool(session_factory=self.db_session_factory),
            RootCauseAnalysisTool(session_factory=self.db_session_factory),
            NotificationDrafterTool()
        ]
        
        if self.llm_config.get("provider") == "bedrock":
            self.llm = BedrockChat(
                model_id=self.llm_config.get("model_name", "anthropic.claude-v2"),
                model_kwargs={"temperature": self.llm_config.get("temperature", 0.0)}
            )
        else:
            self.llm = ChatOpenAI(
                model=self.llm_config.get("model_name", "gpt-4-turbo"),
                temperature=self.llm_config.get("temperature", 0.0)
            )
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True,
            return_intermediate_steps=True
        )

    async def query(self, user_message: str, conversation_id: str = None) -> AgentResponse:
        try:
            result = await self.agent_executor.ainvoke({"input": user_message})
            
            output_text = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            sources = []
            data = None
            vis_type = None
            
            for action, observation in intermediate_steps:
                sources.append(f"Tool {action.tool}: {action.tool_input}")
                
                if action.tool == "supplier_history":
                    try:
                        obs_data = json.loads(observation)
                        if "history" in obs_data:
                            data = {"history": obs_data["history"]}
                            vis_type = "line_chart"
                    except json.JSONDecodeError:
                        pass
                elif action.tool == "sql_query":
                    data = {"sql_result": observation}
                    vis_type = "table"
            
            return AgentResponse(
                text=output_text,
                data=data,
                visualization_type=vis_type,
                sources=sources
            )
        except Exception as e:
            logger.error(f"Agent error: {e}")
            return AgentResponse(
                text=f"An error occurred while processing your request: {str(e)}",
                data=None,
                visualization_type=None,
                sources=[]
            )
