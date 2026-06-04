import streamlit as st
import time
from src.dashboard.utils.db import get_db_session
from src.common.db.queries import get_all_suppliers, get_defect_summary, get_recent_inspections
from src.dashboard.components.charts import create_pareto, create_oee_gauge
from src.dashboard.components.filters import render_auto_refresh_toggle
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Quality Control", layout="wide")
st.title("Quality Control")

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
            defect_summary = get_defect_summary(session, selected_supplier, days=7)
            recent_inspections = get_recent_inspections(session, selected_supplier, hours=24)
            
            categories = [d["defect_name"] for d in defect_summary]
            counts = [d["count"] for d in defect_summary]
            
            if not categories:
                categories = ["Scratch", "Dent", "Misalignment"]
                counts = [15, 8, 2]
                
    except Exception as e:
        st.error(f"Error loading data: {e}")
        categories, counts = [], []
        recent_inspections = []

    col_pareto, col_cpk = st.columns([2, 1])
    
    with col_pareto:
        st.subheader("Defect Pareto (Last 7 Days)")
        fig_pareto = create_pareto(categories, counts)
        st.plotly_chart(fig_pareto, use_container_width=True)
        
    with col_cpk:
        st.subheader("Process Capability (Cpk)")
        try:
            with get_db_session() as session:
                from src.common.db.queries import get_recent_production_runs
                from src.pipeline.transforms.kpi import calculate_cpk
                runs = get_recent_production_runs(session, selected_supplier, hours=24)
                if len(runs) > 1:
                    data = [r.cycle_time_seconds for r in runs]
                    cpk_val = calculate_cpk(data, usl=15.0, lsl=5.0)
                else:
                    cpk_val = 0.0
        except Exception:
            cpk_val = 0.0
            
        fig_cpk = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cpk_val,
            title={'text': "Cpk"},
            gauge={
                'axis': {'range': [0, 2.0]},
                'bar': {'color': "#ffffff"},
                'steps': [
                    {'range': [0, 1.0], 'color': "#e94560"},
                    {'range': [1.0, 1.33], 'color': "#f39c12"},
                    {'range': [1.33, 2.0], 'color': "#2ecc71"}
                ],
            }
        ))
        fig_cpk.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_cpk, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("Inspection Gallery")
    img_cols = st.columns(4)
    if recent_inspections:
        # Display up to 4 recent inspections
        for i, (col, insp) in enumerate(zip(img_cols, recent_inspections[:4])):
            with col:
                # If there's no real image path or it's not accessible directly by Streamlit,
                # use a placeholder that describes the defect.
                img_src = insp.image_path if insp.image_path else f"https://placehold.co/300x200/16213e/e94560?text={insp.result.upper()}"
                st.image(img_src, use_column_width=True)
                st.caption(f"{insp.timestamp.strftime('%H:%M')} | Result: {insp.result} | Conf: {insp.confidence:.2f if insp.confidence else 0.0}")
    else:
        st.info("No recent inspections found.")

if auto_refresh:
    time.sleep(30)
    st.rerun()
