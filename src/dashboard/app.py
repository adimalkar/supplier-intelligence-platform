import streamlit as st

# Set page config
st.set_page_config(
    page_title="SIE Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    /* Tesla-inspired dark theme overrides */
    .stApp {
        background-color: #1a1a2e;
        color: #ffffff;
    }
    .css-1d391kg {
        background-color: #16213e;
    }
    /* Headers */
    h1, h2, h3 {
        color: #e94560 !important;
    }
    /* Metrics */
    .css-1xarl3l {
        background-color: #0f3460;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric label {
        color: #a0a0a0 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    /* SideBar */
    .css-1y4p8pa {
        padding-top: 2rem;
    }
    /* Primary buttons */
    .stButton>button {
        background-color: #e94560;
        color: white;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #c83b52;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("SIE Analytics Platform")
st.markdown("Welcome to the Supplier Intelligence Platform Dashboard. Please select a page from the sidebar.")
