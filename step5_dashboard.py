"""
=============================================================
  STEP 5 — INTERACTIVE STREAMLIT DASHBOARD
=============================================================
  What this script does:
  - Creates a complete web dashboard in your browser
  - Shows KPI metrics, interactive charts, and data tables
  - Allows filtering by country and debt category

  For beginners:
  - Streamlit turns Python code into a live web app instantly
  - Every time you change a filter, the page auto-updates
  - No HTML/CSS/JavaScript needed!

  HOW TO RUN:
    streamlit run step5_dashboard.py

  This opens a browser tab at: http://localhost:8501
=============================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page Configuration — Must be FIRST streamlit command ─────
st.set_page_config(
    page_title="International Debt Analysis",
    page_icon="🌍",
    layout="wide",              # Use full screen width
    initial_sidebar_state="expanded"
)

# ── Custom CSS for better styling ────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a3a5c;
        text-align: center;
        padding: 10px 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 25px;
    }
    .metric-card {
        background: #f0f4f8;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1a3a5c;
    }
    .insight-box {
        background: #e8f4f8;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 5px 0;
        border-left: 4px solid #2980b9;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================
#  LOAD DATA
# ==============================================================
@st.cache_data   # Cache means data is loaded once, not reloaded every click
def load_data():
    df = pd.read_csv("data/cleaned_debt.csv")
    return df

df = load_data()

# Pre-compute aggregations
country_debt = (
    df.groupby("country_name")["debt"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
country_debt.columns = ["country_name", "total_debt"]

indicator_debt = (
    df.groupby("indicator_name")["debt"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
indicator_debt.columns = ["indicator_name", "total_debt"]

total_global = df["debt"].sum()

# Debt categories using quartiles
p75 = country_debt["total_debt"].quantile(0.75)
p25 = country_debt["total_debt"].quantile(0.25)

def categorize(debt):
    if debt >= p75:   return "High Debt"
    elif debt >= p25: return "Medium Debt"
    else:             return "Low Debt"

country_debt["category"] = country_debt["total_debt"].apply(categorize)
country_debt["pct_global"] = (country_debt["total_debt"] / total_global * 100).round(2)


# ==============================================================
#  SIDEBAR — FILTERS
# ==============================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Globe_icon_2.svg/120px-Globe_icon_2.svg.png", width=80)
    st.title("🔧 Filters")
    st.markdown("---")

    # Country multi-select filter
    all_countries = sorted(df["country_name"].unique())
    selected_countries = st.multiselect(
        "🌍 Select Countries",
        options=all_countries,
        default=all_countries[:10],   # Default: first 10 countries
        help="Hold Ctrl to select multiple countries"
    )

    st.markdown("---")

    # Debt category filter
    selected_categories = st.multiselect(
        "🏷️ Debt Category",
        options=["High Debt", "Medium Debt", "Low Debt"],
        default=["High Debt", "Medium Debt", "Low Debt"]
    )

    st.markdown("---")

    # Indicator filter
    all_indicators = sorted(df["indicator_name"].unique())
    selected_indicator = st.selectbox(
        "📌 Focus on Indicator",
        options=["All Indicators"] + all_indicators
    )

    st.markdown("---")
    st.caption("📊 International Debt Analytics System")
    st.caption("Data Source: World Bank")


# ==============================================================
#  APPLY FILTERS
# ==============================================================
if not selected_countries:
    selected_countries = all_countries   # If none selected, show all

filtered_df     = df[df["country_name"].isin(selected_countries)]
filtered_ctry   = country_debt[
    (country_debt["country_name"].isin(selected_countries)) &
    (country_debt["category"].isin(selected_categories))
]

if selected_indicator != "All Indicators":
    filtered_df = filtered_df[filtered_df["indicator_name"] == selected_indicator]


# ==============================================================
#  HEADER
# ==============================================================
st.markdown('<p class="main-header">🌍 International Debt Analysis Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">World Bank International Debt Statistics — Interactive Analytics</p>', unsafe_allow_html=True)


# ==============================================================
#  ROW 1: KPI METRIC CARDS
# ==============================================================
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

total_filtered = filtered_df["debt"].sum()
num_selected   = filtered_df["country_name"].nunique()
num_indicators = filtered_df["indicator_name"].nunique()
avg_debt       = filtered_df["debt"].mean()
max_country    = filtered_ctry.iloc[0]["country_name"] if len(filtered_ctry) > 0 else "N/A"

col1.metric("💰 Total Debt",       f"${total_filtered/1e9:.1f}B")
col2.metric("🏳️ Countries",        f"{num_selected}")
col3.metric("📌 Indicators",       f"{num_indicators}")
col4.metric("📈 Avg Debt/Record",  f"${avg_debt/1e6:.1f}M")
col5.metric("🏆 Top Country",      max_country)

st.markdown("---")


# ==============================================================
#  ROW 2: TOP COUNTRIES CHART + PIE CHART
# ==============================================================
st.markdown("### 🏆 Country-wise Debt Analysis")
col_left, col_right = st.columns([3, 2])

with col_left:
    # ── Bar Chart: Top Countries ─────────────────────────────
    top_n = st.slider("Show Top N Countries", 5, 20, 10)
    chart_data = filtered_ctry.head(top_n).copy()
    chart_data["debt_b"] = chart_data["total_debt"] / 1e9

    fig_bar = px.bar(
        chart_data,
        x="total_debt",
        y="country_name",
        orientation="h",
        color="category",
        color_discrete_map={
            "High Debt":   "#e74c3c",
            "Medium Debt": "#f39c12",
            "Low Debt":    "#2ecc71"
        },
        labels={"total_debt": "Total Debt (USD)", "country_name": "Country"},
        title=f"Top {top_n} Countries by Total Debt",
        text=chart_data["debt_b"].apply(lambda x: f"${x:.1f}B"),
        hover_data={"pct_global": True}
    )
    fig_bar.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=True,
        height=420,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    # ── Pie Chart: Debt Share ────────────────────────────────
    top5 = filtered_ctry.head(5)
    other_debt = filtered_ctry.iloc[5:]["total_debt"].sum()
    pie_df = pd.concat([
        top5[["country_name", "total_debt"]],
        pd.DataFrame([{"country_name": "All Others", "total_debt": other_debt}])
    ], ignore_index=True)

    fig_pie = px.pie(
        pie_df,
        names="country_name",
        values="total_debt",
        title="Debt Share — Top 5 vs Others",
        hole=0.4,   # Donut chart
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=420, showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")


# ==============================================================
#  ROW 3: INDICATOR ANALYSIS + SCATTER
# ==============================================================
st.markdown("### 📌 Indicator Analysis")
col_a, col_b = st.columns(2)

with col_a:
    # ── Horizontal Bar: Indicators ───────────────────────────
    ind_filtered = (
        filtered_df.groupby("indicator_name")["debt"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )
    ind_filtered["short"] = ind_filtered["indicator_name"].str[:40] + "..."

    fig_ind = px.bar(
        ind_filtered,
        x="debt",
        y="short",
        orientation="h",
        title="Total Debt by Indicator Type",
        color="debt",
        color_continuous_scale="RdYlGn_r",
        labels={"debt": "Total Debt (USD)", "short": "Indicator"}
    )
    fig_ind.update_layout(
        height=420,
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_ind, use_container_width=True)

with col_b:
    # ── Treemap: Country-Indicator ───────────────────────────
    treemap_df = (
        filtered_df.groupby(["country_name", "indicator_code"])["debt"]
        .sum()
        .reset_index()
    )
    treemap_df = treemap_df[treemap_df["debt"] > 0]

    fig_tree = px.treemap(
        treemap_df,
        path=["country_name", "indicator_code"],
        values="debt",
        title="Treemap — Country → Indicator Breakdown",
        color="debt",
        color_continuous_scale="Blues"
    )
    fig_tree.update_layout(height=420)
    st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")


# ==============================================================
#  ROW 4: HEATMAP
# ==============================================================
st.markdown("### 🔥 Debt Heatmap — Countries × Indicators")

pivot = filtered_df.pivot_table(
    index="country_name",
    columns="indicator_code",
    values="debt",
    aggfunc="sum"
).fillna(0) / 1e9  # Convert to billions

fig_heat = px.imshow(
    pivot,
    color_continuous_scale="YlOrRd",
    title="Debt Values (Billions USD) — Country vs Indicator",
    labels={"color": "Debt (B USD)"},
    aspect="auto"
)
fig_heat.update_layout(height=500)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")


# ==============================================================
#  ROW 5: DATA TABLE + DOWNLOAD
# ==============================================================
st.markdown("### 📋 Detailed Data Table")

col_t1, col_t2 = st.columns([2, 1])

with col_t1:
    # Show country summary table
    display_ctry = filtered_ctry.copy()
    display_ctry["total_debt"] = display_ctry["total_debt"].apply(lambda x: f"${x/1e9:.2f}B")
    display_ctry["pct_global"] = display_ctry["pct_global"].apply(lambda x: f"{x}%")
    display_ctry.columns = ["Country", "Total Debt", "Category", "Global %"]
    st.dataframe(display_ctry, use_container_width=True, height=300)

with col_t2:
    st.markdown("#### 🔑 Key Insights")
    insights = [
        f"📍 Highest debt: <b>{filtered_ctry.iloc[0]['country_name']}</b>" if len(filtered_ctry) > 0 else "",
        f"📉 Lowest debt: <b>{filtered_ctry.iloc[-1]['country_name']}</b>" if len(filtered_ctry) > 0 else "",
        f"💰 Total analysed: <b>${total_filtered/1e9:.1f}B</b>",
        f"📊 High-debt countries: <b>{len(filtered_ctry[filtered_ctry['category']=='High Debt'])}</b>",
        f"🌐 Countries >5% share: <b>{len(filtered_ctry[filtered_ctry['pct_global']>5])}</b>",
        f"📌 Top indicator: <b>{indicator_debt.iloc[0]['indicator_name'][:35]}...</b>",
    ]
    for ins in insights:
        if ins:
            st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)

# ── Download Button ──────────────────────────────────────────
st.markdown("---")
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data (CSV)",
        data=csv_data,
        file_name="filtered_debt_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_dl2:
    summary_csv = filtered_ctry.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Country Summary (CSV)",
        data=summary_csv,
        file_name="country_debt_summary.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")
st.caption("🌍 International Debt Analysis System | Built with Python · Streamlit · Plotly")
