import streamlit as st
from datetime import date, timedelta
from typing import Tuple, List

def render_date_range_picker(key: str = "date_range") -> Tuple[date, date]:
    """Render a date range picker."""
    today = date.today()
    default_start = today - timedelta(days=7)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=default_start, key=f"{key}_start")
    with col2:
        end_date = st.date_input("End Date", value=today, key=f"{key}_end")
        
    return start_date, end_date

def render_supplier_multi_select(supplier_codes: List[str], key: str = "suppliers") -> List[str]:
    """Render a multi-select for suppliers."""
    return st.multiselect(
        "Select Suppliers",
        options=supplier_codes,
        default=supplier_codes,
        key=key
    )

def render_auto_refresh_toggle(key: str = "auto_refresh") -> bool:
    """Render an auto-refresh toggle."""
    return st.toggle("Auto-Refresh (30s)", value=True, key=key)
