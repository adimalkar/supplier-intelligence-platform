import streamlit as st
import time
from src.dashboard.utils.db import get_db_session
from src.common.db.queries import get_all_suppliers, get_equipment_for_supplier, get_recent_equipment_events
from src.dashboard.components.filters import render_auto_refresh_toggle
from src.dashboard.components.charts import create_oee_gauge
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Equipment Monitoring", layout="wide")
st.title("Equipment Monitoring")

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
            equipment = get_equipment_for_supplier(session, selected_supplier)
            eq_codes = [e.equipment_code for e in equipment]
    except Exception as e:
        st.error(f"Error loading equipment: {e}")
        eq_codes = []
        
    if eq_codes:
        selected_eq = st.selectbox("Select Equipment", options=eq_codes)
        
        try:
            with get_db_session() as session:
                events = get_recent_equipment_events(session, selected_eq, hours=1)
        except Exception as e:
            events = []

        st.markdown("---")
        
        # Sensor Gauges
        st.subheader("Live Sensor Telemetry")
        col_t, col_p, col_v, col_oee = st.columns(4)
        
        # Real telemetry from latest event
        if events:
            latest_event = events[0]
            temp = latest_event.temperature_c if latest_event.temperature_c is not None else 0.0
            pressure = latest_event.pressure_psi if latest_event.pressure_psi is not None else 0.0
            vibration = latest_event.vibration_mm_s if latest_event.vibration_mm_s is not None else 0.0
        else:
            temp = 0.0
            pressure = 0.0
            vibration = 0.0
            
        # For OEE, we'd ideally fetch from fact_production_runs. Using a placeholder if missing.
        # Could be improved to query actual OEE for this equipment.
        eq_oee = 0.0
        
        def create_sensor_gauge(val, title, max_val, unit):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                title={'text': title},
                number={'suffix': f" {unit}"},
                gauge={'axis': {'range': [0, max_val]}}
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=250, margin=dict(l=10, r=10, t=30, b=10))
            return fig

        with col_t:
            st.plotly_chart(create_sensor_gauge(temp, "Temperature", 100, "°C"), use_container_width=True)
        with col_p:
            st.plotly_chart(create_sensor_gauge(pressure, "Pressure", 200, "PSI"), use_container_width=True)
        with col_v:
            st.plotly_chart(create_sensor_gauge(vibration, "Vibration", 5.0, "mm/s"), use_container_width=True)
        with col_oee:
            # We can use our standard OEE gauge
            st.plotly_chart(create_oee_gauge(eq_oee, "Equipment OEE"), use_container_width=True)
            
        st.markdown("---")
        
        col_downtime, col_maint = st.columns(2)
        
        with col_downtime:
            st.subheader("Downtime Analysis")
            # Mock downtime
            categories = ["Planned", "Unplanned", "Changeover", "Idle"]
            values = [10, 45, 20, 25]
            fig_dt = go.Figure(data=[go.Pie(labels=categories, values=values, hole=.3)])
            fig_dt.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_dt, use_container_width=True)
            
        with col_maint:
            st.subheader("Maintenance Timeline")
            # Mock maintenance events
            if events:
                df_events = pd.DataFrame([{"Time": e.timestamp, "Event": e.event_type} for e in events])
            else:
                now = datetime.now()
                df_events = pd.DataFrame([
                    {"Time": now - timedelta(hours=2), "Event": "Calibration"},
                    {"Time": now - timedelta(days=1), "Event": "Part Replacement"},
                    {"Time": now - timedelta(days=5), "Event": "Monthly PM"}
                ])
            st.dataframe(df_events, use_container_width=True, hide_index=True)

    else:
        st.info("No equipment found for this supplier.")

if auto_refresh:
    time.sleep(30)
    st.rerun()
