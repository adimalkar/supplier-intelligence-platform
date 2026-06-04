import streamlit as st
import time
from datetime import date, timedelta
from src.dashboard.utils.db import get_db_session
from src.common.db.queries import get_all_suppliers, get_supplier_kpis, get_equipment_for_supplier, get_recent_production_runs
from src.dashboard.components.charts import create_oee_gauge, create_spc_chart
from src.dashboard.components.filters import render_auto_refresh_toggle
import pandas as pd
import numpy as np

st.set_page_config(page_title="Supplier Detail", layout="wide")
st.title("Supplier Detail")

try:
    with get_db_session() as session:
        suppliers = get_all_suppliers(session)
        supplier_codes = [s.supplier_code for s in suppliers]
except Exception as e:
    st.error("Could not load suppliers.")
    supplier_codes = []

col1, col2 = st.columns([3, 1])
with col1:
    selected_supplier = st.selectbox("Select Supplier", options=supplier_codes)
with col2:
    auto_refresh = render_auto_refresh_toggle()

if selected_supplier:
    try:
        with get_db_session() as session:
            kpis = get_supplier_kpis(session, selected_supplier)
            equipment = get_equipment_for_supplier(session, selected_supplier)
            recent_runs = get_recent_production_runs(session, selected_supplier, hours=24)
            
            # Extract yield trend for SPC chart
            # We will use the recent runs to plot yield
            recent_runs = sorted(recent_runs, key=lambda x: x.timestamp)
            yield_dates = [r.timestamp.strftime("%H:%M") for r in recent_runs[-20:]]
            yield_values = [r.yield_rate * 100 for r in recent_runs[-20:]]
            
            # No need to mock if empty, UI handles it below
            if yield_values:
                mean_yield = np.mean(yield_values)
                std_yield = np.std(yield_values)
                ucl = mean_yield + 3 * std_yield
                lcl = mean_yield - 3 * std_yield
            else:
                mean_yield, std_yield, ucl, lcl = 0, 0, 0, 0

    except Exception as e:
        st.error(f"Error loading data: {e}")
        kpis = {}
        equipment = []
        yield_dates, yield_values = [], []

    # Layout
    col_kpi1, col_kpi2 = st.columns([1, 2])
    
    with col_kpi1:
        st.subheader("OEE Status")
        oee_val = kpis.get("avg_oee") or 0.0
        fig_oee = create_oee_gauge(oee_val)
        st.plotly_chart(fig_oee, use_container_width=True)
        
    with col_kpi2:
        st.subheader("Yield Trend (SPC)")
        if yield_values:
            fig_spc = create_spc_chart(yield_dates, yield_values, ucl, lcl, mean_yield, "Yield % over Last 24 Hours")
            st.plotly_chart(fig_spc, use_container_width=True)
        else:
            st.info("No yield data available.")
            
    st.markdown("---")
    
    col_eq, col_corr = st.columns(2)
    
    with col_eq:
        st.subheader("Equipment Status")
        if equipment:
            eq_data = [{"Equipment Code": eq.equipment_code, "Type": eq.equipment_type, "Status": eq.status} for eq in equipment]
            st.dataframe(pd.DataFrame(eq_data), use_container_width=True, hide_index=True)
        else:
            st.info("No equipment found.")
            
    with col_corr:
        st.subheader("Process Parameters Correlation")
        # Extract process_params from recent_runs if available
        param_data = []
        for run in recent_runs:
            if run.process_params:
                row = run.process_params.copy()
                row["Yield"] = run.yield_rate
                param_data.append(row)
                
        if len(param_data) > 1:
            import plotly.express as px
            df_params = pd.DataFrame(param_data)
            # Select only numeric columns for correlation
            df_numeric = df_params.select_dtypes(include=[np.number])
            if not df_numeric.empty and df_numeric.shape[1] > 1:
                corr_matrix = df_numeric.corr()
                fig_corr = px.imshow(corr_matrix, color_continuous_scale="RdBu", aspect="auto")
                fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("Not enough numeric process parameters for correlation.")
        else:
            st.info("Correlation matrix requires process_params from telemetry. (Waiting for real data)")
            # In a real scenario, we'd extract process_params from telemetry/runs
            mock_corr = pd.DataFrame(
                np.random.rand(4, 4),
                columns=["Temp", "Pressure", "Vibration", "Yield"],
                index=["Temp", "Pressure", "Vibration", "Yield"]
            )
            import plotly.express as px
            fig_corr = px.imshow(mock_corr, color_continuous_scale="RdBu", aspect="auto")
            fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig_corr, use_container_width=True)

if auto_refresh:
    time.sleep(30)
    st.rerun()
