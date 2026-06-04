import re
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class SQLQueryInput(BaseModel):
    query: str = Field(description="The SQL query to execute. Must be a SELECT statement.")

class SQLQueryTool(BaseTool):
    name: str = "sql_query"
    description: str = "Executes a read-only SQL query against the database."
    args_schema: Type[BaseModel] = SQLQueryInput
    session_factory: Any = None

    def __init__(self, session_factory: Any, **kwargs):
        super().__init__(**kwargs)
        self.session_factory = session_factory

    def _run(self, query: str, run_manager: Optional[Any] = None) -> str:
        query_upper = query.upper()
        forbidden_keywords = ["DROP", "UPDATE", "INSERT", "DELETE", "ALTER", "GRANT", "REVOKE", "TRUNCATE"]
        for keyword in forbidden_keywords:
            if re.search(rf"\b{keyword}\b", query_upper):
                return f"Error: The SQL query contains forbidden keyword '{keyword}'. Only SELECT queries are allowed."
        
        if not re.search(r"^\s*SELECT\b", query_upper):
            return "Error: The SQL query must be a SELECT statement."
        
        try:
            with self.session_factory() as session:
                # postgres statement timeout 30s
                session.execute(text("SET statement_timeout = '30000'"))
                result = session.execute(text(query))
                rows = result.fetchall()
                keys = result.keys()
                
                if not rows:
                    return "No results found."
                
                output = []
                output.append(" | ".join([str(k) for k in keys]))
                output.append("-" * len(output[0]))
                
                for row in rows:
                    output.append(" | ".join([str(v) for v in row]))
                
                return "\n".join(output)
        except SQLAlchemyError as e:
            return f"Database error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, query: str, run_manager: Optional[Any] = None) -> str:
        return self._run(query, run_manager)
