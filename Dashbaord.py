import streamlit as st
import pandas as pd
import datetime
from pathlib import Path
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------------
# PATHS – CLOUD + LOCAL FRIENDLY
# ---------------------------------------------------------------------------------
# Base directory of this script (repo folder on Streamlit Cloud)
BASE_DIR = Path(__file__).resolve().parent

# Files must be in the same repo (you already have Adidas.xlsx and adidas-logo.jpg there)
DATA_PATH = BASE_DIR / "Adidas.xlsx"
LOGO_PATH = BASE_DIR / "adidas-logo.jpg"

# ---------------------------------------------------------------------------------
# BASIC PAGE SETUP
# ---------------------------------------------------------------------------------
st.set_page_config(
    page_title="Adidas Interactive Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    div.block-container{
        padding-top:1rem;
        padding-bottom:1rem;
    }
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #020617 40%, #0b1120 100%);
        color: #ffffff;
    }
    /* Cards */
    .metric-card {
        padding: 15px 20px;
        border-radius: 14px;
        background: radial-gradient(circle at top left, #1d4ed8 0, #020617 55%);
        box-shadow: 0 10px 25px rgba(15,23,42,0.7);
        border: 1px solid rgba(148,163,184,0.5);
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #e5e7eb;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
    }
    .metric-sub {
        font-size: 0.7rem;
        color: #cbd5f5;
    }
    /* Section titles */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e5e7eb;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin: 0.4rem 0 0.2rem 0;
    }
    .section-subtitle {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-bottom: 0.5rem;
    }
    /* Download buttons */
    .stDownloadButton > button {
        border-radius: 999px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------------
@st.cache_data
def load_data(path: Path):
    if not path.exists():
        st.error(f"❌ Could not find data file at:\n\n{path}")
        st.stop()

    df_ = pd.read_excel(path)

    # Ensure proper date type
    if "InvoiceDate" in df_.columns:
        df_["InvoiceDate"] = pd.to_datetime(df_["InvoiceDate"])
        df_["Year"] = df_["InvoiceDate"].dt.year
        df_["Month_Year"] = df_["InvoiceDate"].dt.strftime("%b '%y")
    return df_

df = load_data(DATA_PATH)

# --- rest of your code stays EXACTLY the same ---
