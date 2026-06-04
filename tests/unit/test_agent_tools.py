import pytest
import json
from unittest.mock import MagicMock, patch
from src.agentic_ai.tools.sql_query import SQLQueryTool
from src.agentic_ai.tools.supplier_history import SupplierHistoryTool
from src.agentic_ai.tools.root_cause import RootCauseAnalysisTool
from src.agentic_ai.tools.notification import NotificationDrafterTool
from src.agentic_ai.agent import SupplierIntelligenceAgent

def test_sql_query_tool_rejects_drop():
    tool = SQLQueryTool(session_factory=MagicMock())
    result = tool._run("DROP TABLE dim_suppliers;")
    assert "Error" in result
    assert "forbidden keyword" in result

def test_sql_query_tool_rejects_update():
    tool = SQLQueryTool(session_factory=MagicMock())
    result = tool._run("UPDATE dim_suppliers SET name = 'Test';")
    assert "Error" in result
    assert "forbidden keyword" in result

def test_sql_query_tool_allows_select():
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [(1, "Test Supplier")]
    mock_result.keys.return_value = ["id", "name"]
    
    mock_session.execute.return_value = mock_result
    mock_session_factory = MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=mock_session), __exit__=MagicMock()))
    
    tool = SQLQueryTool(session_factory=mock_session_factory)
    result = tool._run("SELECT * FROM dim_suppliers;")
    
    assert "Error" not in result
    assert "id | name" in result
    assert "1 | Test Supplier" in result
    
    # Check if timeout is set
    execute_calls = mock_session.execute.call_args_list
    assert "statement_timeout" in str(execute_calls[0])

@patch("src.agentic_ai.tools.supplier_history.get_supplier_kpis")
def test_supplier_history_tool(mock_get_supplier_kpis):
    mock_get_supplier_kpis.return_value = {"oee": 0.85}
    
    mock_session_factory = MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock()))
    
    tool = SupplierHistoryTool(session_factory=mock_session_factory)
    result = tool._run("ABC", "oee", 7)
    
    assert "history" in result
    
    data = json.loads(result)
    assert len(data["history"]) == 8 # 7 days + today
    assert data["history"][0]["value"] == 0.85

def test_root_cause_analysis_tool():
    tool = RootCauseAnalysisTool(session_factory=MagicMock())
    result = tool._run("SUP-001", "yield drop")
    
    data = json.loads(result)
    assert "hypothesis" in data
    assert data["supplier_code"] == "SUP-001"
    assert "confidence" in data

def test_notification_drafter_tool():
    tool = NotificationDrafterTool()
    result = tool._run("SUP-001", "yield drop", "Fix it immediately")
    
    data = json.loads(result)
    assert "subject" in data
    assert "SUP-001" in data["subject"]
    assert "quality@sup-001.com" == data["to"]

@patch("src.agentic_ai.agent.ChatOpenAI")
def test_supplier_intelligence_agent_init(mock_chat_openai):
    agent = SupplierIntelligenceAgent(db_session_factory=MagicMock(), llm_config={"provider": "openai", "model_name": "gpt-4", "temperature": 0.0})
    assert len(agent.tools) == 4
    assert agent.llm_config["provider"] == "openai"
