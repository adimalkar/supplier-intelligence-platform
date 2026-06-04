FEW_SHOT_EXAMPLES = [
    {
        "input": "What is the OEE for Supplier ABC?",
        "tool": "SupplierHistoryTool",
        "tool_input": {"supplier_code": "ABC", "metric": "oee"}
    },
    {
        "input": "Write an email to Supplier XYZ about their recent drop in yield.",
        "tool": "NotificationDrafterTool",
        "tool_input": {"supplier_code": "XYZ", "issue_description": "recent drop in yield"}
    },
    {
        "input": "Why did the yield drop for Supplier DEF yesterday?",
        "tool": "RootCauseAnalysisTool",
        "tool_input": {"supplier_code": "DEF", "event_description": "yield drop yesterday"}
    },
    {
        "input": "Show me the top 5 suppliers by production volume.",
        "tool": "SQLQueryTool",
        "tool_input": {"query": "SELECT s.supplier_code, SUM(p.units_produced) FROM fact_production_runs p JOIN dim_suppliers s ON p.supplier_id = s.supplier_id GROUP BY s.supplier_code ORDER BY SUM(p.units_produced) DESC LIMIT 5"}
    }
]
