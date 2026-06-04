import streamlit as st
import time
from datetime import date, timedelta
from src.dashboard.utils.db import get_db_session
from src.common.db.queries import get_all_supplier_kpis, get_all_suppliers, get_recent_production_runs
from src.dashboard.components.kpi_cards import render_kpi_row
from src.dashboard.components.charts import create_heatmap
from src.dashboard.components.filters import render_date_range_picker, render_auto_refresh_toggle
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Overview", layout="wide")

st.title("Enterprise Overview")

# Filters
col1, col2 = st.columns([3, 1])
with col1:
    start_date, end_date = render_date_range_picker()
with col2:
    auto_refresh = render_auto_refresh_toggle()

# Fetch data
try:
    with get_db_session() as session:
        kpis = get_all_supplier_kpis(session, target_date=end_date)
        suppliers = get_all_suppliers(session)
        # We need volume timeline, maybe just using recent runs
        # But this is just an overview. Let's mock the timeline if we can't get it easily,
        # or aggregate runs.
        
        # We also need alert summary cards. Let's calculate total defects from kpis
        total_defects = sum(k['defect_count'] for k in kpis)
        avg_oee = sum(k['avg_oee'] or 0 for k in kpis) / len(kpis) if kpis else 0
        total_produced = sum(k['total_units_produced'] for k in kpis)
except Exception as e:
    st.error(f"Database connection error: {e}")
    kpis = []
    total_defects = 0
    avg_oee = 0
    total_produced = 0

# KPI Cards
st.subheader("Global Metrics")
render_kpi_row([
    {"title": "Average OEE", "value": f"{avg_oee*100:.1f}%"},
    {"title": "Total Units Produced", "value": f"{total_produced:,}"},
    {"title": "Total Alerts (Defects)", "value": f"{total_defects}"}
])

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Supplier Performance Heatmap")
    if kpis:
        sup_names = [k['supplier_code'] for k in kpis]
        metrics = ['OEE', 'Yield', 'Defect Count']
        data = []
        for k in kpis:
            oee_score = (k['avg_oee'] or 0) * 100
            yield_score = (k['avg_yield'] or 0) * 100
            # Normalize defect count inversely for heatmap if needed, but let's just show raw for now
            # Actually, the heatmap needs a score. Let's map defect count to a 0-100 scale where 0 is 100
            defect_score = max(0, 100 - k['defect_count']) 
            data.append([oee_score, yield_score, defect_score])
            
        fig_heat = create_heatmap(sup_names, metrics, data)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("No supplier data available.")

with col_right:
    st.subheader("Production Volume Timeline")
    if total_produced > 0:
        try:
            with get_db_session() as session:
                from sqlalchemy import text
                # Fetch actual 7-day volume trend
                query = text("""
                    SELECT date_trunc('day', timestamp) as day, sum(units_produced) as volume
                    FROM fact_production_runs
                    WHERE timestamp >= :start_date
                    GROUP BY 1
                    ORDER BY 1
                """)
                start_date_filter = end_date - timedelta(days=6)
                result = session.execute(query, {"start_date": start_date_filter}).fetchall()
                
                if result:
                    df_vol = pd.DataFrame([{"Date": r.day, "Volume": r.volume} for r in result])
                    fig_vol = px.line(df_vol, x='Date', y='Volume', markers=True, title="7-Day Production Volume")
                    fig_vol.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                    st.plotly_chart(fig_vol, use_container_width=True)
                else:
                    st.info("No timeline data available.")
        except Exception as e:
            st.error(f"Error loading timeline: {e}")
    else:
        st.info("No production data available.")

if auto_refresh:
    time.sleep(30)
    st.rerun()
