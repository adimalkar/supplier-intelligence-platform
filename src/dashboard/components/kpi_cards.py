import streamlit as st
from typing import List, Dict, Any

def render_kpi_card(title: str, value: Any, delta: str | None = None) -> None:
    """Render a single KPI card using Streamlit metrics."""
    st.metric(label=title, value=value, delta=delta)

def render_kpi_row(kpis: List[Dict[str, Any]]) -> None:
    """
    Render a row of KPI cards.
    kpis is a list of dicts: [{"title": "OEE", "value": "85%", "delta": "2%"}]
    """
    cols = st.columns(len(kpis))
    for i, col in enumerate(cols):
        with col:
            kpi = kpis[i]
            render_kpi_card(kpi["title"], kpi["value"], kpi.get("delta"))
