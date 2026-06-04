import streamlit as st
import time
from src.dashboard.utils.db import get_db_session
from src.common.db.queries import get_all_suppliers, get_alert_history
from src.dashboard.components.filters import render_auto_refresh_toggle
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Alerts Hub", layout="wide")
st.title("Alerts Hub")

try:
    with get_db_session() as session:
        suppliers = get_all_suppliers(session)
        supplier_codes = ["All"] + [s.supplier_code for s in suppliers]
except Exception as e:
    st.error("Could not load suppliers.")
    supplier_codes = ["All"]

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    selected_supplier = st.selectbox("Filter by Supplier", options=supplier_codes)
with col2:
    selected_severity = st.multiselect("Severity", options=["critical", "high", "medium", "low"], default=["critical", "high", "medium", "low"])
with col3:
    auto_refresh = render_auto_refresh_toggle()

try:
    with get_db_session() as session:
        sup_filter = None if selected_supplier == "All" else selected_supplier
        alerts = get_alert_history(session, sup_filter, hours=24)
        
        if alerts:
            df_alerts = pd.DataFrame(alerts)
            # Filter by severity if applicable
            if "severity" in df_alerts.columns:
                df_alerts["severity"] = df_alerts["severity"].fillna("medium")
            else:
                df_alerts["severity"] = "medium"
                
            df_alerts = df_alerts[df_alerts["severity"].isin(selected_severity)]
        else:
            df_alerts = pd.DataFrame()
            
except Exception as e:
    st.error(f"Error loading alerts: {e}")
    df_alerts = pd.DataFrame()

col_pie, col_feed = st.columns([1, 2])

with col_pie:
    st.subheader("Severity Distribution")
    if not df_alerts.empty:
        severity_counts = df_alerts["severity"].value_counts().reset_index()
        severity_counts.columns = ["Severity", "Count"]
        
        color_map = {
            "critical": "#e94560",
            "high": "#f39c12",
            "medium": "#f1c40f",
            "low": "#3498db"
        }
        
        fig = px.pie(severity_counts, values="Count", names="Severity", color="Severity", color_discrete_map=color_map)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No alerts matching criteria.")

with col_feed:
    st.subheader("Alert Timeline")
    if not df_alerts.empty:
        # Sort by timestamp
        df_alerts = df_alerts.sort_values(by="timestamp", ascending=False)
        
        for idx, row in df_alerts.iterrows():
            with st.expander(f"[{row.get('severity', 'unknown').upper()}] {row.get('timestamp', '')} - {row.get('defect_name', 'Alert')}"):
                st.write(f"**Supplier:** {row.get('supplier_code', 'N/A')}")
                st.write(f"**Inspection Type:** {row.get('inspection_type', 'N/A')}")
                st.write(f"**Confidence:** {row.get('confidence', 'N/A')}")
                
                if st.button("Acknowledge", key=f"ack_{idx}"):
                    st.success("Alert acknowledged.")
    else:
        st.info("No alerts matching criteria.")

if auto_refresh:
    time.sleep(30)
    st.rerun()
