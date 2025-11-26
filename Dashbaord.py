# Dashbaord.py

import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import streamlit as st

# ------------------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Adidas Interactive Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# PATHS (WORK LOCALLY & ON STREAMLIT CLOUD)
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "Adidas.xlsx"
LOGO_PATH = BASE_DIR / "adidas-logo.jpg"

# ------------------------------------------------------------------------------
# GLOBAL STYLES
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    div.block-container{
        padding-top:1rem;
        padding-bottom:1rem;
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #020617 40%, #0b1120 100%);
        color: #ffffff;
    }
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
    .stDownloadButton > button {
        border-radius: 999px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# LOAD & CLEAN DATA
# ------------------------------------------------------------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"❌ Could not find data file at:\n\n{path}")
        st.stop()

    df_ = pd.read_excel(path)

    # --- Normalize column names we use later so app doesn't crash ---
    cols = df_.columns

    # Invoice date
    if "Invoice Date" in cols and "InvoiceDate" not in cols:
        df_["InvoiceDate"] = pd.to_datetime(df_["Invoice Date"])
    elif "InvoiceDate" in cols:
        df_["InvoiceDate"] = pd.to_datetime(df_["InvoiceDate"], errors="coerce")

    # Total sales
    if "Total Sales" in cols and "TotalSales" not in cols:
        df_["TotalSales"] = df_["Total Sales"]

    # Units sold
    if "Units Sold" in cols and "UnitsSold" not in cols:
        df_["UnitsSold"] = df_["Units Sold"]

    # Sales method
    if "Sales Method" in cols and "SalesMethod" not in cols:
        df_["SalesMethod"] = df_["Sales Method"]

    # Time fields
    if "InvoiceDate" in df_.columns:
        df_["Year"] = df_["InvoiceDate"].dt.year
        df_["Month_Year"] = df_["InvoiceDate"].dt.strftime("%b '%y")

    return df_


df = load_data(DATA_PATH)

# ------------------------------------------------------------------------------
# HEADER (TITLE + LOGO)
# ------------------------------------------------------------------------------
if LOGO_PATH.exists():
    image = Image.open(LOGO_PATH)
else:
    image = None
    st.warning(f"⚠ Logo not found at: {LOGO_PATH}. The app will still work without the image.")

col_logo, col_title = st.columns([0.12, 0.88])

with col_logo:
    if image is not None:
        st.image(image, width=110)

with col_title:
    html_title = """
    <div style="padding: 5px 10px; border-radius: 12px; background: linear-gradient(90deg,#1d4ed8,#22c55e);">
        <h1 style="color:white; text-align:center; margin:0; font-size:2.1rem;">
            Adidas Interactive Sales Intelligence Hub
        </h1>
    </div>
    """
    st.markdown(html_title, unsafe_allow_html=True)
    box_date = datetime.datetime.now().strftime("%d %B %Y")
    st.markdown(
        f"<p style='color:#9ca3af; margin-top:0.3rem;'>Last refreshed on <b>{box_date}</b></p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ------------------------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------------------------
with st.sidebar:
    if image is not None:
        st.image(image)
    st.markdown(
        "<h3 style='color:white;'>🔍 Filter Your View</h3>",
        unsafe_allow_html=True,
    )

    # Region filter
    if "Region" in df.columns:
        region_list = sorted(df["Region"].dropna().unique())
        selected_region = st.multiselect("Region", region_list, default=region_list)
    else:
        region_list, selected_region = [], []

    # Retailer filter
    if "Retailer" in df.columns:
        retailer_list = sorted(df["Retailer"].dropna().unique())
        selected_retailer = st.multiselect("Retailer", retailer_list, default=retailer_list)
    else:
        retailer_list, selected_retailer = [], []

    # State filter
    if "State" in df.columns:
        state_list = sorted(df["State"].dropna().unique())
        selected_state = st.multiselect("State", state_list, default=state_list)
    else:
        state_list, selected_state = [], []

    # Date range filter
    if "InvoiceDate" in df.columns:
        min_date = df["InvoiceDate"].min()
        max_date = df["InvoiceDate"].max()
        date_range = st.date_input(
            "Invoice Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    else:
        date_range = None

# Apply filters
df_filtered = df.copy()

if region_list:
    df_filtered = df_filtered[df_filtered["Region"].isin(selected_region)]

if retailer_list:
    df_filtered = df_filtered[df_filtered["Retailer"].isin(selected_retailer)]

if state_list:
    df_filtered = df_filtered[df_filtered["State"].isin(selected_state)]

if date_range is not None and "InvoiceDate" in df_filtered.columns:
    if isinstance(date_range, tuple):
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
    else:  # user picked only one date
        start_date = pd.to_datetime(date_range)
        end_date = start_date + pd.Timedelta(days=1)

    df_filtered = df_filtered[
        (df_filtered["InvoiceDate"] >= start_date) & (df_filtered["InvoiceDate"] < end_date)
    ]

# ------------------------------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------------------------------
total_sales = df_filtered["TotalSales"].sum() if "TotalSales" in df_filtered.columns else 0
total_units = df_filtered["UnitsSold"].sum() if "UnitsSold" in df_filtered.columns else 0
total_orders = len(df_filtered)
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Total Revenue</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">${total_sales:,.0f}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-sub">Sum of Total Sales</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_kpi2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Units Sold</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{int(total_units):,}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-sub">All Products</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_kpi3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Number of Invoices</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{total_orders:,}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-sub">Transactions in Selection</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_kpi4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Avg. Order Value</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">${avg_order_value:,.0f}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-sub">TotalSales / Invoices</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

# ------------------------------------------------------------------------------
# ROW 1 – RETAILER & TIME SERIES
# ------------------------------------------------------------------------------
col3, col4 = st.columns([0.52, 0.48])

# Sales by Retailer
with col3:
    st.markdown('<div class="section-title">Sales by Retailer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Compare which partners drive the most revenue.</div>',
        unsafe_allow_html=True,
    )

    if {"Retailer", "TotalSales"}.issubset(df_filtered.columns):
        data_retailer = (
            df_filtered.groupby("Retailer")["TotalSales"]
            .sum()
            .reset_index()
            .sort_values("TotalSales", ascending=False)
        )

        if not data_retailer.empty:
            fig_retailer = px.bar(
                data_retailer,
                x="Retailer",
                y="TotalSales",
                labels={"TotalSales": "Total Sales ($)", "Retailer": "Retailer"},
                color="TotalSales",
                color_continuous_scale="Viridis",
                template="plotly_dark",
                height=430,
            )
            fig_retailer.update_layout(
                xaxis_title="Retailer",
                yaxis_title="Total Sales ($)",
                bargap=0.25,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_retailer, use_container_width=True)

            exp1, dwn1 = st.columns([0.6, 0.4])
            with exp1:
                expander = st.expander("📊 Retailer-wise Sales Data")
                expander.write(data_retailer)
            with dwn1:
                st.download_button(
                    "⬇ Download Retailer Data",
                    data_retailer.to_csv(index=False).encode("utf-8"),
                    file_name="RetailerSales.csv",
                    mime="text/csv",
                )
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.info("Required columns (Retailer, TotalSales) not found in dataset.")

# Sales Trend Over Time
with col4:
    st.markdown('<div class="section-title">Sales Trend Over Time</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Track how revenue evolves across months.</div>',
        unsafe_allow_html=True,
    )

    if {"Month_Year", "TotalSales"}.issubset(df_filtered.columns):
        result_time = (
            df_filtered.groupby("Month_Year")["TotalSales"]
            .sum()
            .reset_index()
            .sort_values("Month_Year")
        )

        if not result_time.empty:
            fig_time = px.line(
                result_time,
                x="Month_Year",
                y="TotalSales",
                markers=True,
                labels={"TotalSales": "Total Sales ($)", "Month_Year": "Month"},
                template="plotly_dark",
                height=430,
            )
            fig_time.update_traces(line=dict(width=3))
            fig_time.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_time, use_container_width=True)

            exp2, dwn2 = st.columns([0.6, 0.4])
            with exp2:
                expander = st.expander("📊 Monthly Sales Data")
                expander.write(result_time)
            with dwn2:
                st.download_button(
                    "⬇ Download Monthly Sales Data",
                    result_time.to_csv(index=False).encode("utf-8"),
                    file_name="MonthlySales.csv",
                    mime="text/csv",
                )
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.info("Invoice date information not available for time-series chart.")

st.markdown("---")

# ------------------------------------------------------------------------------
# ROW 2 – STATE PERFORMANCE & PRODUCT/METHOD ANALYSIS
# ------------------------------------------------------------------------------
col5, col6 = st.columns([0.55, 0.45])

# State performance with combo chart
with col5:
    st.markdown('<div class="section-title">State Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">View sales and units sold by state in one glance.</div>',
        unsafe_allow_html=True,
    )

    if {"State", "TotalSales", "UnitsSold"}.issubset(df_filtered.columns):
        result_state = (
            df_filtered.groupby("State")[["TotalSales", "UnitsSold"]]
            .sum()
            .reset_index()
            .sort_values("TotalSales", ascending=False)
        )

        if not result_state.empty:
            fig_state = go.Figure()
            fig_state.add_trace(
                go.Bar(
                    x=result_state["State"],
                    y=result_state["TotalSales"],
                    name="Total Sales ($)",
                )
            )
            fig_state.add_trace(
                go.Scatter(
                    x=result_state["State"],
                    y=result_state["UnitsSold"],
                    name="Units Sold",
                    mode="lines+markers",
                    yaxis="y2",
                )
            )

            fig_state.update_layout(
                template="plotly_dark",
                height=450,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(title="State"),
                yaxis=dict(title="Total Sales ($)", showgrid=False),
                yaxis2=dict(
                    title="Units Sold",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )
            st.plotly_chart(fig_state, use_container_width=True)

            exp3, dwn3 = st.columns([0.6, 0.4])
            with exp3:
                expander = st.expander("📊 State-wise Sales & Units Data")
                expander.write(result_state)
            with dwn3:
                st.download_button(
                    "⬇ Download State Data",
                    result_state.to_csv(index=False).encode("utf-8"),
                    file_name="Sales_by_State.csv",
                    mime="text/csv",
                )
        else:
            st.warning("No state-level data available for current filters.")
    else:
        st.info("State / TotalSales / UnitsSold columns not available.")

# Product & Sales Method analysis
with col6:
    st.markdown('<div class="section-title">Product & Sales Mix</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Which products or channels dominate revenue?</div>',
        unsafe_allow_html=True,
    )

    # Top products
    if {"Product", "TotalSales"}.issubset(df_filtered.columns):
        prod_data = (
            df_filtered.groupby("Product")["TotalSales"]
            .sum()
            .reset_index()
            .sort_values("TotalSales", ascending=False)
            .head(10)
        )

        if not prod_data.empty:
            fig_prod = px.bar(
                prod_data,
                x="TotalSales",
                y="Product",
                orientation="h",
                labels={"TotalSales": "Total Sales ($)", "Product": "Product"},
                color="TotalSales",
                color_continuous_scale="Plasma",
                template="plotly_dark",
                height=260,
                title="Top 10 Products by Sales",
            )
            fig_prod.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_prod, use_container_width=True)

    # Sales method pie
    if {"SalesMethod", "TotalSales"}.issubset(df_filtered.columns):
        method_data = (
            df_filtered.groupby("SalesMethod")["TotalSales"]
            .sum()
            .reset_index()
        )

        if not method_data.empty:
            fig_method = px.pie(
                method_data,
                names="SalesMethod",
                values="TotalSales",
                template="plotly_dark",
                hole=0.45,
                title="Sales Share by Method",
                height=260,
            )
            fig_method.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_method, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------------------
# ROW 3 – TREEMAP & RAW DATA
# ------------------------------------------------------------------------------
col7, col8 = st.columns([0.6, 0.4])

with col7:
    st.markdown('<div class="section-title">Region & City Heatmap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Drill into the Adidas footprint across regions and cities.</div>',
        unsafe_allow_html=True,
    )

    if {"Region", "City", "TotalSales"}.issubset(df_filtered.columns):
        treemap = (
            df_filtered[["Region", "City", "TotalSales"]]
            .groupby(["Region", "City"])["TotalSales"]
            .sum()
            .reset_index()
        )

        if not treemap.empty:

            def format_sales(value):
                if pd.isna(value):
                    return ""
                if value >= 1_000_000:
                    return f"${value / 1_000_000:,.1f} M"
                if value >= 1_000:
                    return f"${value / 1_000:,.1f} K"
                return f"${value:,.0f}"

            treemap["TotalSales (Formatted)"] = treemap["TotalSales"].apply(format_sales)

            fig_tree = px.treemap(
                treemap,
                path=["Region", "City"],
                values="TotalSales",
                hover_data=["TotalSales (Formatted)"],
                color="Region",
                template="plotly_dark",
                height=540,
            )
            fig_tree.update_traces(textinfo="label+value")
            st.plotly_chart(fig_tree, use_container_width=True)

            exp4, dwn4 = st.columns([0.6, 0.4])
            with exp4:
                expander = st.expander("📊 Region & City Sales Data")
                expander.write(
                    treemap[["Region", "City", "TotalSales", "TotalSales (Formatted)"]]
                )
            with dwn4:
                st.download_button(
                    "⬇ Download Region-City Data",
                    treemap.to_csv(index=False).encode("utf-8"),
                    file_name="Sales_by_Region_City.csv",
                    mime="text/csv",
                )
        else:
            st.warning("No region/city data available for current filters.")
    else:
        st.info("Region / City / TotalSales columns not available for Treemap.")

with col8:
    st.markdown('<div class="section-title">Raw Dataset (Filtered)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Inspect individual transactions behind the charts.</div>',
        unsafe_allow_html=True,
    )

    exp_raw = st.expander("📄 View Raw Data")
    exp_raw.write(df_filtered)

    st.download_button(
        "⬇ Download Filtered Raw Data",
        df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="Adidas_Sales_Filtered.csv",
        mime="text/csv",
    )

st.markdown("---")

# ------------------------------------------------------------------------------
# FOOTNOTE
# ------------------------------------------------------------------------------
st.markdown(
    """
    <p style="color:#9ca3af; font-size:0.85rem; text-align:center; margin-top:0.5rem;">
    💡 <b>Tip:</b> Use the filters in the left sidebar to create custom stories:
    compare retailers, zoom into a specific region, or analyze only a particular time window.
    </p>
    """,
    unsafe_allow_html=True,
)
