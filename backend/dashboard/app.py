import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import io
import warnings
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
#  1. PAGE CONFIG  ─  must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Ledger — Startup Funding Intelligence",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  2. PATH RESOLUTION
# ─────────────────────────────────────────────
BASE_DIR           = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH          = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.csv')
RAW_DATA_PATH      = os.path.join(BASE_DIR, 'data', 'raw', 'Startup_Funding_Cleaned.csv')
NETWORK_PATH       = os.path.join(BASE_DIR, 'data', 'processed', 'investor_network_edges.csv')
CENTRALITY_PATH    = os.path.join(BASE_DIR, 'data', 'processed', 'investor_centrality.csv')
SUCCESS_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'success_model.pkl')
FUNDING_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'funding_model.pkl')

# ─────────────────────────────────────────────
#  3. DATA LOADERS (cached)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_main_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, low_memory=False)
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_raw_data():
    if os.path.exists(RAW_DATA_PATH):
        df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
        if 'funded_at' in df.columns:
            df['funded_at'] = pd.to_datetime(df['funded_at'], errors='coerce')
            df['fund_year'] = df['funded_at'].dt.year
            df['fund_month'] = df['funded_at'].dt.month
            df['fund_quarter'] = df['funded_at'].dt.quarter
        return df
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_network_data():
    if os.path.exists(NETWORK_PATH):
        return pd.read_csv(NETWORK_PATH)
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_centrality_data():
    if os.path.exists(CENTRALITY_PATH):
        return pd.read_csv(CENTRALITY_PATH)
    return pd.DataFrame()

@st.cache_resource(show_spinner=False)
def load_models():
    success_model, funding_model = None, None
    if os.path.exists(SUCCESS_MODEL_PATH):
        with open(SUCCESS_MODEL_PATH, 'rb') as f:
            success_model = pickle.load(f)
    if os.path.exists(FUNDING_MODEL_PATH):
        with open(FUNDING_MODEL_PATH, 'rb') as f:
            funding_model = pickle.load(f)
    return success_model, funding_model

with st.spinner("Loading data..."):
    df           = load_main_data()
    raw_df       = load_raw_data()
    network_df   = load_network_data()
    centrality_df= load_centrality_data()
    success_model, funding_model = load_models()

# ─────────────────────────────────────────────
#  4. GLOBAL CSS  ─  Dark Indigo Premium Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #07071a;
    color: #e0e0f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e0e28 0%, #0a0a1f 100%);
    border-right: 1px solid #1e1e40;
}
section[data-testid="stSidebar"] .stRadio > label {
    color: #9090b8 !important;
    font-size: 0.84rem !important;
}

/* Main area */
.main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

/* ── KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #12122e 0%, #16163a 100%);
    border: 1px solid #2c2c58;
    border-radius: 16px;
    padding: 22px 18px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    box-shadow: 0 4px 24px rgba(91,141,239,0.06);
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #5B8DEF, #8E5BEF);
    opacity: 0.6;
    border-radius: 16px 16px 0 0;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(91,141,239,0.20);
    border-color: #4a4a90;
}
.kpi-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: #5B8DEF;
    line-height: 1.1;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}
.kpi-value.green  { color: #5BEFB8; }
.kpi-value.purple { color: #8E5BEF; }
.kpi-value.rose   { color: #EF5B8D; }
.kpi-value.gold   { color: #EFB85B; }
.kpi-value.cyan   { color: #5BE8EF; }
.kpi-label {
    font-size: 0.76rem;
    color: #6868a0;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.kpi-delta {
    font-size: 0.78rem;
    color: #5BEFB8;
    margin-top: 4px;
    font-weight: 500;
}
.kpi-delta.neg { color: #EF5B8D; }

/* ── Section headers */
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #c0c0ea;
    padding: 10px 0 6px 0;
    border-bottom: 1px solid #1e1e40;
    margin-bottom: 14px;
    letter-spacing: 0.01em;
}

/* ── Insight boxes */
.insight-box {
    background: #0f0f2e;
    border-left: 3px solid #5B8DEF;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.87rem;
    color: #c0c0e0;
    line-height: 1.65;
}
.insight-box.green  { border-left-color: #5BEFB8; }
.insight-box.purple { border-left-color: #8E5BEF; }
.insight-box.rose   { border-left-color: #EF5B8D; }
.insight-box.gold   { border-left-color: #EFB85B; }

/* ── Result cards */
.result-success {
    background: linear-gradient(135deg, #071e14 0%, #051710 100%);
    border: 1px solid #1d5c36;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.result-fail {
    background: linear-gradient(135deg, #1e0f07 0%, #180a04 100%);
    border: 1px solid #5c2a1d;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.result-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; }

/* ── Badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 2px 3px;
}
.badge-blue   { background: rgba(91,141,239,0.15); color: #5B8DEF; border: 1px solid #5B8DEF40; }
.badge-green  { background: rgba(91,239,184,0.15); color: #5BEFB8; border: 1px solid #5BEFB840; }
.badge-purple { background: rgba(142,91,239,0.15); color: #8E5BEF; border: 1px solid #8E5BEF40; }
.badge-gold   { background: rgba(239,184,91,0.15); color: #EFB85B; border: 1px solid #EFB85B40; }
.badge-rose   { background: rgba(239,91,141,0.15); color: #EF5B8D; border: 1px solid #EF5B8D40; }

/* ── Timeline */
.timeline-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid #151535;
}
.timeline-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #5B8DEF;
    margin-top: 4px;
    flex-shrink: 0;
    box-shadow: 0 0 8px #5B8DEF80;
}
.timeline-dot.seed   { background: #EFB85B; box-shadow: 0 0 8px #EFB85B80; }
.timeline-dot.seriesA{ background: #5B8DEF; box-shadow: 0 0 8px #5B8DEF80; }
.timeline-dot.seriesB{ background: #8E5BEF; box-shadow: 0 0 8px #8E5BEF80; }
.timeline-dot.seriesC{ background: #5BEFB8; box-shadow: 0 0 8px #5BEFB880; }
.timeline-dot.other  { background: #EF5B8D; box-shadow: 0 0 8px #EF5B8D80; }
.timeline-content { flex: 1; }
.timeline-title { font-size: 0.92rem; font-weight: 600; color: #d0d0f0; }
.timeline-sub   { font-size: 0.80rem; color: #6060a0; margin-top: 2px; }

/* ── Page divider */
.page-divider {
    border: none;
    border-top: 1px solid #181838;
    margin: 22px 0;
}

/* ── Streamlit metric override */
[data-testid="metric-container"] {
    background: #12122e;
    border: 1px solid #2c2c58;
    border-radius: 12px;
    padding: 16px;
}

/* ── Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Sidebar brand */
.sidebar-brand {
    text-align: center;
    padding: 18px 10px 8px;
}
.sidebar-brand h2 {
    font-size: 1.35rem;
    font-weight: 800;
    background: linear-gradient(135deg, #5B8DEF, #8E5BEF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.sidebar-brand p {
    font-size: 0.72rem;
    color: #505080;
    margin: 4px 0 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Nav item hover */
label[data-baseweb="radio"] span { transition: color 0.15s ease; }
label[data-baseweb="radio"]:hover span { color: #5B8DEF !important; }

/* ── Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, #5B8DEF, #8E5BEF) !important; border-radius: 4px; }

/* ── Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4a7de0, #7a5be0);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
    padding: 10px 28px;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(91,141,239,0.40);
}

/* ── Download button */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #1a4a20, #2a6a30);
    color: #5BEFB8;
    border: 1px solid #2d6b4a;
    border-radius: 10px;
    font-weight: 600;
}

/* ── Selectbox / inputs */
.stSelectbox > div > div {
    background: #12122e !important;
    border-color: #2c2c58 !important;
    color: #d0d0f0 !important;
}

/* ── Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #0e0e28;
    border-radius: 12px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #7070a8;
    font-weight: 500;
    font-size: 0.87rem;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4a7de0, #7a5be0) !important;
    color: white !important;
}

/* ── Opportunity score card */
.opp-card {
    background: linear-gradient(135deg, #0f1a35 0%, #12152e 100%);
    border: 1px solid #2c3a6a;
    border-radius: 14px;
    padding: 18px;
    margin: 6px 0;
    transition: transform 0.2s ease;
}
.opp-card:hover { transform: translateX(4px); }
.opp-rank { font-size: 1.5rem; font-weight: 800; color: #EFB85B; }
.opp-name { font-size: 1.05rem; font-weight: 600; color: #d0d0f8; }
.opp-stat { font-size: 0.80rem; color: #6868a0; margin-top: 4px; }

/* ── Network graph placeholder */
.network-placeholder {
    background: #0a0a20;
    border: 1px dashed #2a2a50;
    border-radius: 14px;
    padding: 40px;
    text-align: center;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

/* ── Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0a20; }
::-webkit-scrollbar-thumb { background: #2a2a5a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a7a; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  5. SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>🌌 Ledger</h2>
        <p>Startup Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigate to",
        [
            "🏠  Executive Overview",
            "📈  Funding Trends",
            "🏭  Sector Intelligence",
            "🌍  Geographic Analysis",
            "🔍  Startup Performance",
            "💰  Funding Stage Analysis",
            "🎯  Investment Opportunities",
            "📅  Funding Timeline",
            "🤝  Investor Network",
            "🔮  Predictive ML Engine",
            "📊  Reports & Export",
            "📋  Data Explorer",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#4a4a80; padding:6px 0;'>
        <b style='color:#5B8DEF;'>Data Status</b>
    </div>
    """, unsafe_allow_html=True)

    def _status_icon(ok): return "🟢" if ok else "🔴"

    st.markdown(f"""
    <div style='font-size:0.78rem; color:#7070a0; line-height:2;'>
    {_status_icon(not df.empty)} Feature Dataset<br>
    {_status_icon(not raw_df.empty)} Raw Round Data<br>
    {_status_icon(not network_df.empty)} Investor Network<br>
    {_status_icon(not centrality_df.empty)} Centrality Data<br>
    {_status_icon(success_model is not None)} Success Model<br>
    {_status_icon(funding_model is not None)} Funding Model
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if not df.empty:
        highest_deal = df['Total_Funding_USD'].max() if 'Total_Funding_USD' in df.columns else 0
        avg_deal     = df['Total_Funding_USD'].mean() if 'Total_Funding_USD' in df.columns else 0
        st.markdown(f"""
        <div style='font-size:0.72rem; color:#4a4a80;'>
            <b style='color:#5B8DEF;'>Quick Stats</b><br><br>
            Companies: <b style='color:#c0c0e0;'>{df['company_id'].nunique() if 'company_id' in df.columns else 'N/A':,}</b><br>
            Rows: <b style='color:#c0c0e0;'>{len(df):,}</b><br>
            Features: <b style='color:#c0c0e0;'>{df.shape[1]}</b><br>
            Highest Deal: <b style='color:#EFB85B;'>${highest_deal/1e6:.0f}M</b><br>
            Avg Deal: <b style='color:#5BEFB8;'>${avg_deal/1e6:.1f}M</b>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════
def safe_fmt(val, fmt="{:,.0f}", fallback="N/A"):
    try:
        return fmt.format(val)
    except Exception:
        return fallback

def _round_type_color(rtype):
    rtype = str(rtype).lower()
    if 'seed' in rtype: return 'seed'
    if 'series-a' in rtype or 'series_a' in rtype: return 'seriesA'
    if 'series-b' in rtype or 'series_b' in rtype: return 'seriesB'
    if 'series-c' in rtype or 'series_c' in rtype: return 'seriesC'
    return 'other'


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 1 — EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════════════════
if page == "🏠  Executive Overview":
    st.title("🚀 Startup Funding Intelligence Dashboard")
    st.caption("Deal-level intelligence across the global startup funding ecosystem.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("⚠️ Feature dataset not found. Please run the notebooks first.")
        st.stop()

    # ── Compute all KPIs upfront
    total_companies  = df['company_id'].nunique()          if 'company_id'           in df.columns else 0
    total_rounds_sum = df['Total_Funding_Rounds'].sum()    if 'Total_Funding_Rounds'  in df.columns else 0
    total_usd        = df['Total_Funding_USD'].sum()       if 'Total_Funding_USD'     in df.columns else 0
    success_rate     = df['is_successful'].mean() * 100    if 'is_successful'         in df.columns else 0
    avg_rounds       = df['Total_Funding_Rounds'].mean()   if 'Total_Funding_Rounds'  in df.columns else 0
    median_fund      = df['Total_Funding_USD'].median()    if 'Total_Funding_USD'     in df.columns else 0
    unique_investors = int(df['Unique_Investors_Count'].sum()) if 'Unique_Investors_Count' in df.columns else 0
    num_countries    = df['country_code_cleaned'].nunique() if 'country_code_cleaned' in df.columns else 0
    # NEW KPIs
    highest_deal     = df['Total_Funding_USD'].max()       if 'Total_Funding_USD'     in df.columns else 0
    avg_deal_size    = df['Total_Funding_USD'].mean()      if 'Total_Funding_USD'     in df.columns else 0
    active_investors = int(centrality_df.shape[0]) if not centrality_df.empty else unique_investors

    # YoY growth from raw data
    yoy_growth = None
    if not raw_df.empty and 'fund_year' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
        yearly = raw_df.dropna(subset=['fund_year','raised_amount_usd'])
        yearly = yearly.groupby('fund_year')['raised_amount_usd'].sum()
        yearly = yearly.sort_index()
        if len(yearly) >= 2:
            last2 = yearly.iloc[-2:]
            if last2.iloc[0] > 0:
                yoy_growth = (last2.iloc[1] - last2.iloc[0]) / last2.iloc[0] * 100

    # City-wise top city
    top_city = "N/A"
    if not raw_df.empty and 'city' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
        city_fund = raw_df.dropna(subset=['city','raised_amount_usd']).groupby('city')['raised_amount_usd'].sum()
        if not city_fund.empty:
            top_city = city_fund.idxmax()

    # ── KPI Row 1 (4 cards)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value">{total_companies:,}</div>
            <div class="kpi-label">Total Tracked Startups</div>
        </div>''', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value purple">{int(total_rounds_sum):,}</div>
            <div class="kpi-label">Total Funding Rounds</div>
        </div>''', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value green">${total_usd/1e9:.2f}B</div>
            <div class="kpi-label">Total Capital Deployed</div>
        </div>''', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value rose">{success_rate:.1f}%</div>
            <div class="kpi-label">Global Exit Success Rate</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI Row 2 (4 cards) – NEW KPIs
    kpi5, kpi6, kpi7, kpi8 = st.columns(4)
    with kpi5:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value gold">${highest_deal/1e6:.0f}M</div>
            <div class="kpi-label">Highest Funding Deal</div>
        </div>''', unsafe_allow_html=True)
    with kpi6:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value cyan">${avg_deal_size/1e6:.1f}M</div>
            <div class="kpi-label">Average Deal Size</div>
        </div>''', unsafe_allow_html=True)
    with kpi7:
        yr_str = f"{yoy_growth:+.1f}%" if yoy_growth is not None else "N/A"
        delta_cls = "" if (yoy_growth is None or yoy_growth >= 0) else "neg"
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value {'green' if (yoy_growth or 0) >= 0 else 'rose'}">{yr_str}</div>
            <div class="kpi-label">Funding YoY Growth Rate</div>
        </div>''', unsafe_allow_html=True)
    with kpi8:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value purple">{active_investors:,}</div>
            <div class="kpi-label">Active Investors</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI Row 3 (4 cards)
    kpi9, kpi10, kpi11, kpi12 = st.columns(4)
    with kpi9:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value gold">{avg_rounds:.1f}</div>
            <div class="kpi-label">Avg Funding Rounds / Startup</div>
        </div>''', unsafe_allow_html=True)
    with kpi10:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value">${median_fund/1e6:.1f}M</div>
            <div class="kpi-label">Median Startup Funding</div>
        </div>''', unsafe_allow_html=True)
    with kpi11:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value green">{num_countries}</div>
            <div class="kpi-label">Countries Covered</div>
        </div>''', unsafe_allow_html=True)
    with kpi12:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value cyan">🏙️ {top_city}</div>
            <div class="kpi-label">Top City by Funding</div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Time-Series Chart (NEW)
    if not raw_df.empty and 'fund_year' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
        st.markdown('<div class="section-header">📅 Annual Funding Volume — Time Series</div>', unsafe_allow_html=True)
        ts1, ts2 = st.columns(2)
        with ts1:
            yearly_vol = (raw_df.dropna(subset=['fund_year','raised_amount_usd'])
                         .groupby('fund_year')['raised_amount_usd']
                         .sum() / 1e9).reset_index()
            yearly_vol.columns = ['Year', 'Capital_Deployed_B']
            yearly_vol = yearly_vol[(yearly_vol['Year'] >= 2000) & (yearly_vol['Year'] <= 2020)]
            st.markdown("**💰 Capital Deployed per Year ($B)**")
            st.area_chart(yearly_vol.set_index('Year'), color='#5B8DEF', height=240)
        with ts2:
            yearly_cnt = (raw_df.dropna(subset=['fund_year'])
                         .groupby('fund_year')['company_id']
                         .nunique()).reset_index()
            yearly_cnt.columns = ['Year', 'Companies_Funded']
            yearly_cnt = yearly_cnt[(yearly_cnt['Year'] >= 2000) & (yearly_cnt['Year'] <= 2020)]
            st.markdown("**🏢 Companies Funded per Year**")
            st.area_chart(yearly_cnt.set_index('Year'), color='#8E5BEF', height=240)
        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Charts row
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">📊 Top 10 Sectors by Company Count</div>', unsafe_allow_html=True)
        if 'Industry_Sector_cleaned' in df.columns:
            sector_data = df['Industry_Sector_cleaned'].value_counts().head(10).reset_index()
            sector_data.columns = ['Sector', 'Count']
            st.bar_chart(sector_data.set_index('Sector'), color='#5B8DEF', height=300)
    with col_r:
        st.markdown('<div class="section-header">🌍 Top 10 Countries by Company Count</div>', unsafe_allow_html=True)
        if 'country_code_cleaned' in df.columns:
            country_data = df['country_code_cleaned'].value_counts().head(10).reset_index()
            country_data.columns = ['Country', 'Count']
            st.bar_chart(country_data.set_index('Country'), color='#8E5BEF', height=300)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── City-wise Funding (NEW)
    if not raw_df.empty and 'city' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
        st.markdown('<div class="section-header">🏙️ City-wise Funding Distribution</div>', unsafe_allow_html=True)
        city_fund = (raw_df.dropna(subset=['city','raised_amount_usd'])
                    .groupby('city')['raised_amount_usd']
                    .sum() / 1e9).sort_values(ascending=False).head(15).reset_index()
        city_fund.columns = ['City', 'Funding_B']
        st.bar_chart(city_fund.set_index('City'), color='#EFB85B', height=300)
        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Key Insights
    st.markdown('<div class="section-header">💡 Key Ecosystem Insights</div>', unsafe_allow_html=True)
    ins1, ins2, ins3 = st.columns(3)
    with ins1:
        top_sector = df['Industry_Sector_cleaned'].value_counts().index[0] if 'Industry_Sector_cleaned' in df.columns else 'N/A'
        st.markdown(f'''<div class="insight-box">
            <b>🏆 Dominant Sector</b><br>
            <span style="color:#5B8DEF; font-size:1.1em"><b>{top_sector.title()}</b></span> leads in total startup count across the ecosystem.
        </div>''', unsafe_allow_html=True)
    with ins2:
        recession_pct = df['Fought_Through_Recession'].mean() * 100 if 'Fought_Through_Recession' in df.columns else 0
        st.markdown(f'''<div class="insight-box green">
            <b>📉 Recession Resilience</b><br>
            <span style="color:#5BEFB8; font-size:1.1em"><b>{recession_pct:.1f}%</b></span> of companies received funding during the 2008–09 recession era.
        </div>''', unsafe_allow_html=True)
    with ins3:
        top_country = df['country_code_cleaned'].value_counts().index[0] if 'country_code_cleaned' in df.columns else 'N/A'
        top_pct = df['country_code_cleaned'].value_counts(normalize=True).iloc[0] * 100 if 'country_code_cleaned' in df.columns else 0
        st.markdown(f'''<div class="insight-box purple">
            <b>🌎 Geographic Leader</b><br>
            <span style="color:#8E5BEF; font-size:1.1em"><b>{top_country}</b></span> accounts for <b>{top_pct:.1f}%</b> of all tracked startups globally.
        </div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 2 — FUNDING TRENDS
# ═══════════════════════════════════════════════════════════════════════
elif page == "📈  Funding Trends":
    st.title("📈 Funding Trends Over Time")
    st.caption("Historical capital deployment patterns, temporal analysis, and time-series trends.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found.")
        st.stop()

    # ── Time-Series: Monthly & Quarterly (NEW)
    if not raw_df.empty and 'funded_at' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
        st.markdown('<div class="section-header">📅 Monthly & Quarterly Funding Trends</div>', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📆 Monthly", "📊 Quarterly", "📈 Annual"])

        with tab1:
            monthly = (raw_df.dropna(subset=['funded_at','raised_amount_usd'])
                      .copy())
            monthly['period'] = monthly['funded_at'].dt.to_period('M').astype(str)
            monthly_agg = monthly.groupby('period')['raised_amount_usd'].sum().reset_index()
            monthly_agg.columns = ['Month', 'Funding_USD']
            monthly_agg = monthly_agg[monthly_agg['Funding_USD'] > 0].tail(96)  # last 8 years
            monthly_agg['Funding_M'] = monthly_agg['Funding_USD'] / 1e6
            st.markdown("**Monthly Capital Deployed ($M) — last 8 years**")
            st.line_chart(monthly_agg.set_index('Month')['Funding_M'], color='#5B8DEF', height=280)

        with tab2:
            if 'fund_year' in raw_df.columns and 'fund_quarter' in raw_df.columns:
                qdf = raw_df.dropna(subset=['fund_year','fund_quarter','raised_amount_usd']).copy()
                qdf['period'] = qdf['fund_year'].astype(int).astype(str) + '-Q' + qdf['fund_quarter'].astype(int).astype(str)
                qdf = qdf[(qdf['fund_year'] >= 2005) & (qdf['fund_year'] <= 2020)]
                qagg = qdf.groupby('period')['raised_amount_usd'].sum() / 1e9
                qagg = qagg.reset_index()
                qagg.columns = ['Quarter', 'Funding_B']
                st.markdown("**Quarterly Capital Deployed ($B)**")
                st.area_chart(qagg.set_index('Quarter'), color='#8E5BEF', height=280)

        with tab3:
            yearly = (raw_df.dropna(subset=['fund_year','raised_amount_usd'])
                     .groupby('fund_year')['raised_amount_usd'].sum() / 1e9)
            yearly = yearly[(yearly.index >= 2000) & (yearly.index <= 2020)].reset_index()
            yearly.columns = ['Year', 'Funding_B']
            st.markdown("**Annual Capital Deployed ($B)**")
            st.bar_chart(yearly.set_index('Year'), color='#5BEFB8', height=280)

        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Funding distribution
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📦 Funding Amount Distribution</div>', unsafe_allow_html=True)
        if 'Total_Funding_USD' in df.columns:
            _clip_val = df['Total_Funding_USD'].quantile(0.99)
            _fund_series = df['Total_Funding_USD'].clip(upper=_clip_val).dropna()
            _fund_bins = pd.cut(_fund_series, bins=10)
            _fund_counts = _fund_bins.value_counts().sort_index()
            _fund_counts.index = [f'${i.left/1e6:.1f}M–${i.right/1e6:.1f}M' for i in _fund_counts.index]
            st.bar_chart(_fund_counts, color='#5B8DEF', height=260)
            st.caption("Clipped at 99th percentile for readability")
    with col2:
        st.markdown('<div class="section-header">📊 Log Funding Distribution (Normalized)</div>', unsafe_allow_html=True)
        if 'Log_Total_Funding' in df.columns:
            _log_series = df['Log_Total_Funding'].dropna()
            _log_bins = pd.cut(_log_series, bins=20)
            _log_counts = _log_bins.value_counts().sort_index()
            _log_counts.index = [f'{i.left:.1f}–{i.right:.1f}' for i in _log_counts.index]
            st.bar_chart(_log_counts, color='#8E5BEF', height=260)
            st.caption("Log(1 + Total Funding USD) — near-normal distribution")

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Funding round stats
    st.markdown('<div class="section-header">🔄 Funding Rounds Statistics</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    if 'Total_Funding_Rounds' in df.columns:
        with r1: st.metric("Min Rounds", f"{df['Total_Funding_Rounds'].min():.0f}")
        with r2: st.metric("Avg Rounds", f"{df['Total_Funding_Rounds'].mean():.2f}")
        with r3: st.metric("Median Rounds", f"{df['Total_Funding_Rounds'].median():.0f}")
        with r4: st.metric("Max Rounds", f"{df['Total_Funding_Rounds'].max():.0f}")

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Funding velocity
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">⚡ Funding Velocity Distribution</div>', unsafe_allow_html=True)
        if 'Funding_Velocity' in df.columns:
            _vel = df['Funding_Velocity'].clip(upper=df['Funding_Velocity'].quantile(0.98)).dropna()
            _vel_bins = pd.cut(_vel, bins=15)
            _vel_counts = _vel_bins.value_counts().sort_index()
            _vel_counts.index = [f'${i.left/1e6:.2f}M–{i.right/1e6:.2f}M' for i in _vel_counts.index]
            st.bar_chart(_vel_counts, color='#5BEFB8', height=260)
            st.caption("Funding USD per year of company activity")
        else:
            _r_counts = df['Total_Funding_Rounds'].clip(upper=15).value_counts().sort_index()
            _r_counts.index = _r_counts.index.astype(str)
            st.bar_chart(_r_counts, color='#5BEFB8', height=260)
            st.caption("Funding rounds per company")
    with col4:
        st.markdown('<div class="section-header">📅 Activity by Company Era</div>', unsafe_allow_html=True)
        era_data = {}
        if 'Fought_Through_Recession' in df.columns:
            era_data['Recession Era (2008-09)'] = int(df['Fought_Through_Recession'].sum())
        if 'Funded_During_Tech_Boom' in df.columns:
            era_data['Tech Boom (2014-21)'] = int(df['Funded_During_Tech_Boom'].sum())
        if 'Funded_Post_COVID' in df.columns:
            era_data['Post-COVID (2021+)'] = int(df['Funded_Post_COVID'].sum())
        if era_data:
            era_df = pd.DataFrame(list(era_data.items()), columns=['Era', 'Count']).set_index('Era')
            st.bar_chart(era_df, color='#EFB85B', height=260)
        else:
            st.info("Era features not available. Run notebook 04 to generate them.")

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── YoY Growth Table
    if not raw_df.empty and 'fund_year' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
        st.markdown('<div class="section-header">📊 Year-over-Year Funding Growth Analysis</div>', unsafe_allow_html=True)
        ydf = (raw_df.dropna(subset=['fund_year','raised_amount_usd'])
               .groupby('fund_year')['raised_amount_usd'].sum() / 1e9)
        ydf = ydf[(ydf.index >= 2000) & (ydf.index <= 2020)].reset_index()
        ydf.columns = ['Year', 'Funding_B']
        ydf['YoY_Growth_%'] = ydf['Funding_B'].pct_change() * 100
        ydf = ydf.dropna().round(2)
        ydf['Year'] = ydf['Year'].astype(int)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**YoY Growth Rate (%)**")
            st.line_chart(ydf.set_index('Year')['YoY_Growth_%'], color='#5BEFB8', height=240)
        with g2:
            st.dataframe(ydf.rename(columns={'Funding_B': 'Capital ($B)', 'YoY_Growth_%': 'YoY Growth (%)'}),
                        use_container_width=True, height=280)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Success vs funding
    st.markdown('<div class="section-header">🎯 Funding vs. Exit Success Analysis</div>', unsafe_allow_html=True)
    if 'is_successful' in df.columns and 'Total_Funding_Rounds' in df.columns:
        _agg_dict = {'count': ('is_successful', 'count'), 'success_rate': ('is_successful', 'mean')}
        if 'Total_Funding_USD' in df.columns:
            _agg_dict['avg_funding'] = ('Total_Funding_USD', 'mean')
        rounds_analysis = df.groupby('Total_Funding_Rounds').agg(**_agg_dict).reset_index()
        rounds_analysis = rounds_analysis[rounds_analysis['Total_Funding_Rounds'] <= 12]
        rounds_analysis['success_pct'] = rounds_analysis['success_rate'] * 100
        col5, col6 = st.columns(2)
        with col5:
            st.markdown("**Success Rate (%) by Number of Funding Rounds**")
            st.line_chart(rounds_analysis.set_index('Total_Funding_Rounds')['success_pct'], color='#5BEFB8', height=240)
        with col6:
            if 'avg_funding' in rounds_analysis.columns:
                st.markdown("**Average Total Funding ($) by Rounds**")
                st.line_chart(rounds_analysis.set_index('Total_Funding_Rounds')['avg_funding'], color='#5B8DEF', height=240)
        st.caption("Shows clear positive correlation: more rounds → higher success probability")


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 3 — SECTOR INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════
elif page == "🏭  Sector Intelligence":
    st.title("🏭 Industry Sector Intelligence")
    st.caption("Deep-dive analysis into funding patterns and success rates across industry verticals.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found.")
        st.stop()

    if 'Industry_Sector_cleaned' in df.columns:
        all_sectors = sorted(df['Industry_Sector_cleaned'].dropna().unique().tolist())
        selected_sector = st.selectbox(
            "🔍 Drill into a specific sector for detailed analysis:",
            ["— All Sectors —"] + all_sectors,
            help="Select a specific sector to zoom in"
        )
        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

        sector_df = df if selected_sector == "— All Sectors —" else df[df['Industry_Sector_cleaned'] == selected_sector]

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value">{sector_df["company_id"].nunique() if "company_id" in sector_df.columns else len(sector_df):,}</div>
                <div class="kpi-label">Companies in Sector</div>
            </div>''', unsafe_allow_html=True)
        with k2:
            total = sector_df['Total_Funding_USD'].sum() if 'Total_Funding_USD' in sector_df.columns else 0
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value green">${total/1e9:.2f}B</div>
                <div class="kpi-label">Total Capital Raised</div>
            </div>''', unsafe_allow_html=True)
        with k3:
            sr = sector_df['is_successful'].mean() * 100 if 'is_successful' in sector_df.columns else 0
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value rose">{sr:.1f}%</div>
                <div class="kpi-label">Exit Success Rate</div>
            </div>''', unsafe_allow_html=True)
        with k4:
            avg_r = sector_df['Total_Funding_Rounds'].mean() if 'Total_Funding_Rounds' in sector_df.columns else 0
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value purple">{avg_r:.1f}</div>
                <div class="kpi-label">Avg Funding Rounds</div>
            </div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">📊 Top Sectors by Company Count</div>', unsafe_allow_html=True)
            sc = df['Industry_Sector_cleaned'].value_counts().head(15).reset_index()
            sc.columns = ['Sector', 'Count']
            st.bar_chart(sc.set_index('Sector'), color='#5B8DEF', height=320)
        with col2:
            st.markdown('<div class="section-header">🏆 Sector Success Rate Leaderboard</div>', unsafe_allow_html=True)
            if 'is_successful' in df.columns:
                ss = df.groupby('Industry_Sector_cleaned').agg(
                    success_rate=('is_successful', 'mean'),
                    count=('is_successful', 'count')
                ).reset_index()
                ss = ss[ss['count'] >= 10].sort_values('success_rate', ascending=False).head(15)
                ss['success_pct'] = (ss['success_rate'] * 100).round(1)
                st.bar_chart(ss.set_index('Industry_Sector_cleaned')['success_pct'], color='#5BEFB8', height=320)
                st.caption("Filtered to sectors with ≥10 companies")

        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

        # Time-series by sector (NEW)
        if not raw_df.empty and 'Industry_Sector' in raw_df.columns and 'fund_year' in raw_df.columns:
            st.markdown('<div class="section-header">📅 Top Sector Funding Trends Over Time</div>', unsafe_allow_html=True)
            top5_sectors = df['Industry_Sector_cleaned'].value_counts().head(5).index.tolist()
            sec_ts = (raw_df[raw_df['Industry_Sector'].isin(top5_sectors)]
                     .dropna(subset=['fund_year','raised_amount_usd'])
                     .groupby(['fund_year','Industry_Sector'])['raised_amount_usd']
                     .sum() / 1e9).reset_index()
            sec_ts = sec_ts[(sec_ts['fund_year'] >= 2000) & (sec_ts['fund_year'] <= 2020)]
            sec_pivot = sec_ts.pivot(index='fund_year', columns='Industry_Sector', values='raised_amount_usd').fillna(0)
            st.area_chart(sec_pivot, height=300)
            st.caption("Top 5 sectors by company count — annual capital deployed ($B)")
            st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">📋 Sector Funding Summary Table</div>', unsafe_allow_html=True)
        if 'Total_Funding_USD' in df.columns and 'Industry_Sector_cleaned' in df.columns:
            agg_dict = {
                'Companies': ('company_id', 'nunique'),
                'Total_Funding_B': ('Total_Funding_USD', lambda x: round(x.sum() / 1e9, 3)),
                'Avg_Funding_M':   ('Total_Funding_USD', lambda x: round(x.mean() / 1e6, 2)),
                'Median_Funding_M':('Total_Funding_USD', lambda x: round(x.median() / 1e6, 2)),
                'Avg_Rounds':      ('Total_Funding_Rounds', lambda x: round(x.mean(), 1)),
                'Success_Rate_%':  ('is_successful', lambda x: round(x.mean() * 100, 1))
            }
            sector_table = df.groupby('Industry_Sector_cleaned').agg(**agg_dict).reset_index()
            sector_table = sector_table.rename(columns={'Industry_Sector_cleaned': 'Sector'})
            sector_table = sector_table.sort_values('Total_Funding_B', ascending=False)
            st.dataframe(sector_table, use_container_width=True, height=380)


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 4 — GEOGRAPHIC ANALYSIS  (with State & City drill-down)
# ═══════════════════════════════════════════════════════════════════════
elif page == "🌍  Geographic Analysis":
    st.title("🌍 Geographic Startup Ecosystem Analysis")
    st.caption("Country, State & City level distribution of startup activity, funding, and exit performance.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found.")
        st.stop()

    # ── Level tabs (NEW: State & City)
    geo_tab1, geo_tab2, geo_tab3 = st.tabs(["🌐 Country Level", "🗺️ State Level", "🏙️ City Level"])

    with geo_tab1:
        if 'country_code_cleaned' in df.columns:
            geo_table = df.groupby('country_code_cleaned').agg(
                Companies   =('company_id', 'nunique'),
                Total_Funding_B=('Total_Funding_USD', lambda x: round(x.sum() / 1e9, 3)),
                Avg_Funding_M  =('Total_Funding_USD', lambda x: round(x.mean() / 1e6, 2)),
                Avg_Rounds     =('Total_Funding_Rounds', lambda x: round(x.mean(), 1)),
                Avg_Investors  =('Unique_Investors_Count', lambda x: round(x.mean(), 1)),
                Success_Rate_Pct=('is_successful', lambda x: round(x.mean() * 100, 1))
            ).reset_index().rename(columns={'country_code_cleaned': 'Country'})
            geo_table = geo_table.sort_values('Total_Funding_B', ascending=False)

            top = geo_table.iloc[0]
            g1, g2, g3, g4 = st.columns(4)
            with g1:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value">🏆 {top["Country"]}</div>
                    <div class="kpi-label">Top Country by Capital</div>
                </div>''', unsafe_allow_html=True)
            with g2:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value green">${top["Total_Funding_B"]:.1f}B</div>
                    <div class="kpi-label">Capital Deployed (Top)</div>
                </div>''', unsafe_allow_html=True)
            with g3:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value purple">{int(top["Companies"]):,}</div>
                    <div class="kpi-label">Startups (Top Country)</div>
                </div>''', unsafe_allow_html=True)
            with g4:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value rose">{top["Success_Rate_Pct"]:.1f}%</div>
                    <div class="kpi-label">Success Rate (Top)</div>
                </div>''', unsafe_allow_html=True)

            st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="section-header">🏦 Total Capital by Country ($B)</div>', unsafe_allow_html=True)
                st.bar_chart(geo_table.set_index('Country')['Total_Funding_B'], color='#5B8DEF', height=300)
            with c2:
                st.markdown('<div class="section-header">🏆 Exit Success Rate by Country (%)</div>', unsafe_allow_html=True)
                st.bar_chart(geo_table.set_index('Country')['Success_Rate_Pct'], color='#5BEFB8', height=300)
            st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">📋 Complete Country Intelligence Table</div>', unsafe_allow_html=True)
            st.dataframe(geo_table, use_container_width=True, height=360)

    with geo_tab2:
        # State-level (NEW)
        st.markdown('<div class="section-header">🗺️ State-Level Funding Analysis</div>', unsafe_allow_html=True)
        if not raw_df.empty and 'state_code' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
            # Filter selector
            sel_country_geo = st.selectbox("Filter by Country", ['ALL'] + sorted(raw_df['country_code'].dropna().unique().tolist()) if 'country_code' in raw_df.columns else ['ALL'], key='state_country')
            state_src = raw_df if sel_country_geo == 'ALL' else raw_df[raw_df['country_code'] == sel_country_geo]
            state_agg = (state_src.dropna(subset=['state_code','raised_amount_usd'])
                        .groupby('state_code')
                        .agg(
                            Total_Funding_B=('raised_amount_usd', lambda x: round(x.sum()/1e9, 3)),
                            Deals=('raised_amount_usd', 'count'),
                            Avg_Deal_M=('raised_amount_usd', lambda x: round(x.mean()/1e6, 2))
                        ).reset_index().rename(columns={'state_code': 'State'}))
            state_agg = state_agg.sort_values('Total_Funding_B', ascending=False)

            s1, s2 = st.columns(2)
            with s1:
                st.markdown("**💰 Top States by Capital Deployed ($B)**")
                st.bar_chart(state_agg.head(15).set_index('State')['Total_Funding_B'], color='#8E5BEF', height=300)
            with s2:
                st.markdown("**🔢 Top States by Deal Count**")
                st.bar_chart(state_agg.head(15).set_index('State')['Deals'], color='#EFB85B', height=300)

            st.dataframe(state_agg, use_container_width=True, height=340)
        else:
            st.info("State-level data requires the raw dataset (`Startup_Funding_Cleaned.csv`).")

    with geo_tab3:
        # City-level (NEW)
        st.markdown('<div class="section-header">🏙️ City-Level Funding Analysis</div>', unsafe_allow_html=True)
        if not raw_df.empty and 'city' in raw_df.columns and 'raised_amount_usd' in raw_df.columns:
            # Filters
            cf1, cf2 = st.columns(2)
            with cf1:
                city_countries = ['ALL'] + sorted(raw_df['country_code'].dropna().unique().tolist()) if 'country_code' in raw_df.columns else ['ALL']
                sel_cc = st.selectbox("Country", city_countries, key='city_country')
            with cf2:
                top_n = st.slider("Show Top N Cities", 5, 30, 15, key='city_n')

            city_src = raw_df if sel_cc == 'ALL' else raw_df[raw_df['country_code'] == sel_cc]
            city_agg = (city_src.dropna(subset=['city','raised_amount_usd'])
                       .groupby('city')
                       .agg(
                           Total_Funding_B=('raised_amount_usd', lambda x: round(x.sum()/1e9, 3)),
                           Deals=('raised_amount_usd', 'count'),
                           Unique_Startups=('company_id', 'nunique'),
                           Avg_Deal_M=('raised_amount_usd', lambda x: round(x.mean()/1e6, 2))
                       ).reset_index().rename(columns={'city': 'City'}))
            city_agg = city_agg.sort_values('Total_Funding_B', ascending=False).head(top_n)

            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown(f"**💰 Top {top_n} Cities by Capital ($B)**")
                st.bar_chart(city_agg.set_index('City')['Total_Funding_B'], color='#5BEFB8', height=300)
            with cc2:
                st.markdown(f"**🏢 Top {top_n} Cities by Startup Count**")
                st.bar_chart(city_agg.set_index('City')['Unique_Startups'], color='#5B8DEF', height=300)

            st.dataframe(city_agg, use_container_width=True, height=340)
        else:
            st.info("City-level data requires the raw dataset (`Startup_Funding_Cleaned.csv`).")


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 5 — STARTUP PERFORMANCE DASHBOARD  (NEW)
# ═══════════════════════════════════════════════════════════════════════
elif page == "🔍  Startup Performance":
    st.title("🔍 Startup Performance Dashboard")
    st.caption("Search for any startup by name and view its complete funding history and performance profile.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found.")
        st.stop()

    # ── Search box
    search_query = st.text_input("🔎 Search Startup by Name", placeholder="e.g. Fitbit, Digg, Airbnb, Uber...")

    if search_query:
        name_col = 'Startup_Name' if 'Startup_Name' in df.columns else None
        results = pd.DataFrame()
        if name_col:
            results = df[df[name_col].str.contains(search_query, case=False, na=False)]

        if results.empty:
            st.warning(f"No startups found matching **'{search_query}'**. Try a different name.")
        else:
            st.success(f"Found **{len(results)}** startup(s) matching '{search_query}'")
            # If multiple results, let user pick
            if len(results) > 1 and name_col:
                names = results[name_col].unique().tolist()
                selected_name = st.selectbox("Select specific startup:", names)
                startup_row = results[results[name_col] == selected_name].iloc[0]
            else:
                startup_row = results.iloc[0]

            st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

            # ── Profile header
            sname = startup_row.get('Startup_Name', 'Unknown')
            sector = startup_row.get('Industry_Sector_cleaned', startup_row.get('Industry_Sector', 'N/A'))
            country = startup_row.get('country_code_cleaned', startup_row.get('country_code', 'N/A'))
            city_val = startup_row.get('city', 'N/A')
            state_val = startup_row.get('state_code', 'N/A')
            status = startup_row.get('Startup_Status', 'N/A')
            is_succ = startup_row.get('is_successful', 0)

            badge_status_cls = 'badge-green' if status == 'acquired' else ('badge-blue' if status == 'operating' else 'badge-rose')
            succ_badge = '<span class="badge badge-green">✅ Successful Exit</span>' if is_succ else '<span class="badge badge-rose">⏳ No Exit Yet</span>'

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #12122e, #181840); border: 1px solid #2c2c60; border-radius: 16px; padding: 24px 28px; margin-bottom: 18px;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #d8d8ff;">{sname}</div>
                <div style="margin-top: 8px;">
                    <span class="badge badge-blue">🏭 {sector.title()}</span>
                    <span class="badge badge-purple">🌍 {country}</span>
                    <span class="badge badge-gold">🏙️ {city_val}, {state_val}</span>
                    <span class="badge {badge_status_cls}">📌 {status.title()}</span>
                    {succ_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── KPIs
            p1, p2, p3, p4 = st.columns(4)
            total_fund = startup_row.get('Total_Funding_USD', 0)
            n_rounds   = startup_row.get('Total_Funding_Rounds', 0)
            n_investors= startup_row.get('Unique_Investors_Count', 0)
            age        = startup_row.get('Age_at_Latest_Round', 0)

            with p1:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value green">${total_fund/1e6:.1f}M</div>
                    <div class="kpi-label">Total Funding Raised</div>
                </div>''', unsafe_allow_html=True)
            with p2:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value purple">{int(n_rounds)}</div>
                    <div class="kpi-label">Funding Rounds</div>
                </div>''', unsafe_allow_html=True)
            with p3:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value gold">{int(n_investors)}</div>
                    <div class="kpi-label">Unique Investors</div>
                </div>''', unsafe_allow_html=True)
            with p4:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value cyan">{int(age)} yrs</div>
                    <div class="kpi-label">Age at Latest Round</div>
                </div>''', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Full round history from raw data
            cid = startup_row.get('company_id', None)
            if not raw_df.empty and cid:
                raw_startup = raw_df[raw_df['company_id'] == cid].copy()
                if not raw_startup.empty:
                    st.markdown('<div class="section-header">📅 Complete Funding Round History</div>', unsafe_allow_html=True)
                    rounds_disp = raw_startup[['funded_at','funding_round_type','raised_amount_usd','Investor_Name']].copy()
                    rounds_disp = rounds_disp.dropna(subset=['funded_at']).sort_values('funded_at')
                    rounds_disp.columns = ['Date', 'Round Type', 'Amount (USD)', 'Investor']
                    rounds_disp['Amount (USD)'] = rounds_disp['Amount (USD)'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
                    rounds_disp['Date'] = rounds_disp['Date'].astype(str)
                    st.dataframe(rounds_disp, use_container_width=True, height=300)

            # ── Comparison vs sector
            st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">📊 Startup vs Sector Benchmark</div>', unsafe_allow_html=True)
            if 'Industry_Sector_cleaned' in df.columns and sector in df['Industry_Sector_cleaned'].values:
                peer_df = df[df['Industry_Sector_cleaned'] == sector]
                cmp1, cmp2, cmp3 = st.columns(3)
                with cmp1:
                    peer_avg = peer_df['Total_Funding_USD'].mean() if 'Total_Funding_USD' in peer_df.columns else 0
                    st.markdown(f'''<div class="insight-box">
                        <b>💰 Funding vs Sector Avg</b><br>
                        This startup: <code>${total_fund/1e6:.1f}M</code><br>
                        Sector avg: <code>${peer_avg/1e6:.1f}M</code><br>
                        <span style="color:{'#5BEFB8' if total_fund >= peer_avg else '#EF5B8D'}">
                        {"▲ Above" if total_fund >= peer_avg else "▼ Below"} average</span>
                    </div>''', unsafe_allow_html=True)
                with cmp2:
                    peer_sr = peer_df['is_successful'].mean() * 100 if 'is_successful' in peer_df.columns else 0
                    st.markdown(f'''<div class="insight-box green">
                        <b>🎯 Success Rate Context</b><br>
                        Startup: <code>{"Successful" if is_succ else "Not yet"}</code><br>
                        Sector avg: <code>{peer_sr:.1f}%</code><br>
                        Companies in sector: <code>{len(peer_df):,}</code>
                    </div>''', unsafe_allow_html=True)
                with cmp3:
                    peer_rounds = peer_df['Total_Funding_Rounds'].mean() if 'Total_Funding_Rounds' in peer_df.columns else 0
                    st.markdown(f'''<div class="insight-box purple">
                        <b>🔄 Rounds Benchmark</b><br>
                        This startup: <code>{int(n_rounds)} rounds</code><br>
                        Sector avg: <code>{peer_rounds:.1f} rounds</code><br>
                        Investors: <code>{int(n_investors)}</code>
                    </div>''', unsafe_allow_html=True)
    else:
        # Show top startups by default
        st.markdown('<div class="section-header">🏆 Top 20 Startups by Total Funding</div>', unsafe_allow_html=True)
        if 'Total_Funding_USD' in df.columns:
            top20 = df.nlargest(20, 'Total_Funding_USD')[
                [c for c in ['Startup_Name','Industry_Sector_cleaned','country_code_cleaned','city',
                             'Total_Funding_USD','Total_Funding_Rounds','Unique_Investors_Count','is_successful']
                 if c in df.columns]
            ].copy()
            top20['Total_Funding_USD'] = top20['Total_Funding_USD'].apply(lambda x: f"${x/1e6:.1f}M")
            top20.index = range(1, len(top20)+1)
            st.dataframe(top20, use_container_width=True, height=520)


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 6 — FUNDING STAGE ANALYSIS  (NEW)
# ═══════════════════════════════════════════════════════════════════════
elif page == "💰  Funding Stage Analysis":
    st.title("💰 Funding Stage Analysis")
    st.caption("Comparative analysis across Seed, Series A, Series B, Series C, Angel, and PE rounds.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if raw_df.empty:
        st.warning("Raw funding round data not found. This page requires `Startup_Funding_Cleaned.csv`.")
        st.stop()

    if 'funding_round_type' not in raw_df.columns:
        st.error("'funding_round_type' column not found in raw data.")
        st.stop()

    # ── Stage mapping
    STAGE_GROUPS = {
        'Seed':     ['seed', 'angel', 'convertible-note'],
        'Series A': ['series-a'],
        'Series B': ['series-b'],
        'Series C': ['series-c'],
        'Series D+': ['series-d', 'series-e', 'series-f', 'series-g', 'series-h'],
        'PE/Venture': ['private-equity', 'venture'],
        'Late Stage': ['post-ipo-equity', 'post-ipo-debt', 'secondary-market', 'grant'],
    }
    STAGE_COLORS = {
        'Seed': '#EFB85B', 'Series A': '#5B8DEF', 'Series B': '#8E5BEF',
        'Series C': '#5BEFB8', 'Series D+': '#EF5B8D', 'PE/Venture': '#5BE8EF', 'Late Stage': '#c0c0e8'
    }

    def map_stage(rtype):
        rtype = str(rtype).lower().strip()
        for stage, keywords in STAGE_GROUPS.items():
            if rtype in keywords:
                return stage
        return 'Other'

    raw_df2 = raw_df.copy()
    raw_df2['Stage'] = raw_df2['funding_round_type'].apply(map_stage)
    raw_df2 = raw_df2[raw_df2['Stage'] != 'Other']

    # ── Stage KPIs
    stage_summary = (raw_df2.dropna(subset=['raised_amount_usd'])
                    .groupby('Stage')
                    .agg(
                        Total_Deals=('raised_amount_usd', 'count'),
                        Total_Capital_B=('raised_amount_usd', lambda x: round(x.sum()/1e9, 2)),
                        Avg_Deal_M=('raised_amount_usd', lambda x: round(x.mean()/1e6, 2)),
                        Median_Deal_M=('raised_amount_usd', lambda x: round(x.median()/1e6, 2)),
                        Unique_Startups=('company_id', 'nunique')
                    ).reset_index())
    stage_order = [s for s in STAGE_GROUPS.keys() if s in stage_summary['Stage'].values]
    stage_summary = stage_summary.set_index('Stage').reindex(stage_order).reset_index().dropna(subset=['Total_Deals'])

    # KPI cards — row 1 (up to 4)
    n_stages = len(stage_summary)
    row1_count = min(n_stages, 4)
    if row1_count > 0:
        cols = st.columns(row1_count)
        for i, row in enumerate(stage_summary.head(4).itertuples()):
            with cols[i]:
                color_map = {'Seed': 'gold', 'Series A': '', 'Series B': 'purple', 'Series C': 'green'}
                cls = color_map.get(row.Stage, 'rose')
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value {cls}">${row.Total_Capital_B}B</div>
                    <div class="kpi-label">{row.Stage} — Total Capital</div>
                    <div class="kpi-delta">{int(row.Total_Deals):,} Deals</div>
                </div>''', unsafe_allow_html=True)

    # KPI cards — row 2 (remaining stages, only if any exist)
    overflow = stage_summary.iloc[4:]
    if len(overflow) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        cols2 = st.columns(min(len(overflow), 4))
        for i, row in enumerate(overflow.head(4).itertuples()):
            with cols2[i]:
                st.markdown(f'''<div class="kpi-card">
                    <div class="kpi-value cyan">${row.Total_Capital_B}B</div>
                    <div class="kpi-label">{row.Stage} — Total Capital</div>
                    <div class="kpi-delta">{int(row.Total_Deals):,} Deals</div>
                </div>''', unsafe_allow_html=True)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Charts
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown('<div class="section-header">📊 Capital by Stage ($B)</div>', unsafe_allow_html=True)
        st.bar_chart(stage_summary.set_index('Stage')['Total_Capital_B'], color='#5B8DEF', height=280)
    with ch2:
        st.markdown('<div class="section-header">🔢 Deal Count by Stage</div>', unsafe_allow_html=True)
        st.bar_chart(stage_summary.set_index('Stage')['Total_Deals'], color='#8E5BEF', height=280)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown('<div class="section-header">💡 Average Deal Size by Stage ($M)</div>', unsafe_allow_html=True)
        st.bar_chart(stage_summary.set_index('Stage')['Avg_Deal_M'], color='#EFB85B', height=260)
    with ch4:
        st.markdown('<div class="section-header">📅 Stage Funding Trends Over Time</div>', unsafe_allow_html=True)
        if 'fund_year' in raw_df2.columns:
            _st2 = raw_df2.dropna(subset=['fund_year','raised_amount_usd']).copy()
            _st2 = _st2[(_st2['fund_year'] >= 2005) & (_st2['fund_year'] <= 2020)]
            stage_ts = (_st2.groupby(['fund_year','Stage'])['raised_amount_usd']
                       .sum() / 1e9).reset_index()
            stage_ts.columns = ['fund_year', 'Stage', 'raised_amount_usd']
            if not stage_ts.empty:
                stage_pivot = stage_ts.pivot(index='fund_year', columns='Stage', values='raised_amount_usd').fillna(0)
                st.area_chart(stage_pivot, height=260)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Sector breakdown by stage
    st.markdown('<div class="section-header">🏭 Sector Distribution by Funding Stage</div>', unsafe_allow_html=True)
    sel_stage = st.selectbox("Select Stage to Drill Into", stage_order)
    stage_sector = (raw_df2[raw_df2['Stage'] == sel_stage]
                   .dropna(subset=['Industry_Sector','raised_amount_usd'])
                   .groupby('Industry_Sector')
                   .agg(Deals=('raised_amount_usd', 'count'), Capital_M=('raised_amount_usd', lambda x: round(x.sum()/1e6, 1)))
                   .sort_values('Capital_M', ascending=False).head(12))
    ss1, ss2 = st.columns(2)
    with ss1:
        st.markdown(f"**Deal Count in {sel_stage}**")
        st.bar_chart(stage_sector['Deals'], color='#5BEFB8', height=260)
    with ss2:
        st.markdown(f"**Capital Raised in {sel_stage} ($M)**")
        st.bar_chart(stage_sector['Capital_M'], color='#EFB85B', height=260)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 Stage Summary Table</div>', unsafe_allow_html=True)
    st.dataframe(stage_summary, use_container_width=True, height=300)


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 7 — INVESTMENT OPPORTUNITIES  (NEW)
# ═══════════════════════════════════════════════════════════════════════
elif page == "🎯  Investment Opportunities":
    st.title("🎯 Investment Opportunity Discovery")
    st.caption("Data-driven filters to discover high-opportunity startups and emerging sectors.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found.")
        st.stop()

    # ── Filters sidebar panel
    st.markdown('<div class="section-header">⚙️ Opportunity Filters</div>', unsafe_allow_html=True)
    flt1, flt2, flt3, flt4 = st.columns(4)

    with flt1:
        sectors_list = ['All'] + sorted(df['Industry_Sector_cleaned'].dropna().unique().tolist()) if 'Industry_Sector_cleaned' in df.columns else ['All']
        opp_sector = st.selectbox("Sector", sectors_list, key='opp_sec')
    with flt2:
        countries_list = ['All'] + sorted(df['country_code_cleaned'].dropna().unique().tolist()) if 'country_code_cleaned' in df.columns else ['All']
        opp_country = st.selectbox("Country", countries_list, key='opp_ctry')
    with flt3:
        min_fund, max_fund = 0, int(df['Total_Funding_USD'].max() / 1e6) if 'Total_Funding_USD' in df.columns else 1000
        fund_range = st.slider("Funding Range ($M)", min_fund, min(max_fund, 5000), (0, 500), key='opp_fund')
    with flt4:
        succ_filter = st.selectbox("Exit Status", ['All', 'Successful', 'Not Exited'], key='opp_succ')

    # ── Apply filters
    opp_df = df.copy()
    if opp_sector != 'All' and 'Industry_Sector_cleaned' in opp_df.columns:
        opp_df = opp_df[opp_df['Industry_Sector_cleaned'] == opp_sector]
    if opp_country != 'All' and 'country_code_cleaned' in opp_df.columns:
        opp_df = opp_df[opp_df['country_code_cleaned'] == opp_country]
    if 'Total_Funding_USD' in opp_df.columns:
        opp_df = opp_df[(opp_df['Total_Funding_USD'] >= fund_range[0]*1e6) & (opp_df['Total_Funding_USD'] <= fund_range[1]*1e6)]
    if succ_filter == 'Successful' and 'is_successful' in opp_df.columns:
        opp_df = opp_df[opp_df['is_successful'] == 1]
    elif succ_filter == 'Not Exited' and 'is_successful' in opp_df.columns:
        opp_df = opp_df[opp_df['is_successful'] == 0]

    # ── Opportunity score  (composite: funding + investors + pagerank)
    if not opp_df.empty:
        _f = opp_df['Total_Funding_USD'] / opp_df['Total_Funding_USD'].max() if 'Total_Funding_USD' in opp_df.columns and opp_df['Total_Funding_USD'].max() > 0 else 0
        _i = opp_df['Unique_Investors_Count'] / opp_df['Unique_Investors_Count'].max() if 'Unique_Investors_Count' in opp_df.columns and opp_df['Unique_Investors_Count'].max() > 0 else 0
        _p = opp_df['Max_Investor_PageRank'] / opp_df['Max_Investor_PageRank'].max() if 'Max_Investor_PageRank' in opp_df.columns and opp_df['Max_Investor_PageRank'].max() > 0 else 0
        opp_df = opp_df.copy()
        opp_df['Opportunity_Score'] = (0.4 * _f + 0.35 * _i + 0.25 * _p).round(4)
        opp_df_sorted = opp_df.sort_values('Opportunity_Score', ascending=False)

        # ── KPIs
        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
        ok1, ok2, ok3, ok4 = st.columns(4)
        with ok1:
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value">{len(opp_df_sorted):,}</div>
                <div class="kpi-label">Matching Startups</div>
            </div>''', unsafe_allow_html=True)
        with ok2:
            total_cap = opp_df_sorted['Total_Funding_USD'].sum() if 'Total_Funding_USD' in opp_df_sorted.columns else 0
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value green">${total_cap/1e9:.2f}B</div>
                <div class="kpi-label">Total Capital (Filtered)</div>
            </div>''', unsafe_allow_html=True)
        with ok3:
            sr = opp_df_sorted['is_successful'].mean() * 100 if 'is_successful' in opp_df_sorted.columns else 0
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value rose">{sr:.1f}%</div>
                <div class="kpi-label">Success Rate (Filtered)</div>
            </div>''', unsafe_allow_html=True)
        with ok4:
            top_score = opp_df_sorted['Opportunity_Score'].max()
            st.markdown(f'''<div class="kpi-card">
                <div class="kpi-value gold">{top_score:.4f}</div>
                <div class="kpi-label">Peak Opportunity Score</div>
            </div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Top opportunities
        st.markdown('<div class="section-header">🏆 Top Investment Opportunities (by Score)</div>', unsafe_allow_html=True)
        top10 = opp_df_sorted.head(10)

        for rank, (_, row) in enumerate(top10.iterrows(), 1):
            name = row.get('Startup_Name', f'Company {rank}')
            sector = row.get('Industry_Sector_cleaned', 'N/A')
            country = row.get('country_code_cleaned', 'N/A')
            funding = row.get('Total_Funding_USD', 0)
            investors = row.get('Unique_Investors_Count', 0)
            opp_score = row.get('Opportunity_Score', 0)
            is_succ = row.get('is_successful', 0)

            bar_pct = int(opp_score * 100)
            badge_cls = 'badge-green' if is_succ else 'badge-rose'
            succ_text = 'Exited' if is_succ else 'Active'

            st.markdown(f"""
            <div class="opp-card">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div class="opp-rank">#{rank}</div>
                    <div style="flex:1">
                        <div class="opp-name">{name}</div>
                        <div class="opp-stat">
                            <span class="badge badge-blue">🏭 {sector.title()}</span>
                            <span class="badge badge-purple">🌍 {country}</span>
                            <span class="badge {badge_cls}">{succ_text}</span>
                        </div>
                        <div class="opp-stat" style="margin-top:6px;">
                            💰 <b style="color:#5BEFB8">${funding/1e6:.1f}M</b> raised &nbsp;|&nbsp;
                            🤝 <b style="color:#8E5BEF">{int(investors)}</b> investors
                        </div>
                    </div>
                    <div style="text-align:right; min-width:100px;">
                        <div style="font-size:1.4rem; font-weight:800; color:#EFB85B;">{opp_score:.4f}</div>
                        <div style="font-size:0.72rem; color:#6060a0; text-transform:uppercase; letter-spacing:0.04em;">Opp Score</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

        # ── Emerging sectors
        st.markdown('<div class="section-header">🚀 Emerging Sectors by Opportunity Score</div>', unsafe_allow_html=True)
        if 'Industry_Sector_cleaned' in opp_df_sorted.columns:
            emg = opp_df_sorted.groupby('Industry_Sector_cleaned').agg(
                Avg_Score=('Opportunity_Score', 'mean'),
                Count=('Opportunity_Score', 'count'),
                Total_Funding_M=('Total_Funding_USD', lambda x: round(x.sum()/1e6, 1))
            ).sort_values('Avg_Score', ascending=False).head(12)
            ec1, ec2 = st.columns(2)
            with ec1:
                st.markdown("**Average Opportunity Score by Sector**")
                st.bar_chart(emg['Avg_Score'], color='#EFB85B', height=280)
            with ec2:
                st.markdown("**Total Capital by Sector ($M)**")
                st.bar_chart(emg['Total_Funding_M'], color='#5B8DEF', height=280)

        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
        # Full table
        st.markdown('<div class="section-header">📋 Full Filtered Opportunities Table</div>', unsafe_allow_html=True)
        disp_cols = [c for c in ['Startup_Name','Industry_Sector_cleaned','country_code_cleaned','city',
                                 'Total_Funding_USD','Total_Funding_Rounds','Unique_Investors_Count',
                                 'is_successful','Opportunity_Score'] if c in opp_df_sorted.columns]
        st.dataframe(opp_df_sorted[disp_cols].head(200), use_container_width=True, height=400)
    else:
        st.warning("No startups match the current filters. Try adjusting the criteria.")


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 8 — FUNDING TIMELINE  (NEW)
# ═══════════════════════════════════════════════════════════════════════
elif page == "📅  Funding Timeline":
    st.title("📅 Startup Funding Timeline")
    st.caption("Chronological timeline of funding rounds — filter by startup, sector, or date range.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if raw_df.empty:
        st.warning("Raw funding data not found. This page requires `Startup_Funding_Cleaned.csv`.")
        st.stop()

    if 'funded_at' not in raw_df.columns:
        st.error("'funded_at' column not found.")
        st.stop()

    # ── Filters
    tf1, tf2, tf3 = st.columns(3)
    with tf1:
        tl_sector = st.selectbox(
            "Sector",
            ['All'] + sorted(raw_df['Industry_Sector'].dropna().unique().tolist()) if 'Industry_Sector' in raw_df.columns else ['All'],
            key='tl_sec'
        )
    with tf2:
        tl_country = st.selectbox(
            "Country",
            ['All'] + sorted(raw_df['country_code'].dropna().unique().tolist()) if 'country_code' in raw_df.columns else ['All'],
            key='tl_ctry'
        )
    with tf3:
        year_range = st.slider("Year Range", 2000, 2020, (2005, 2015), key='tl_yr')

    # Search startup
    tl_search = st.text_input("🔎 Search Startup (optional)", placeholder="e.g. Fitbit, Airbnb...", key='tl_srch')

    # Apply filters
    tl_df = raw_df.dropna(subset=['funded_at','fund_year']).copy()
    tl_df = tl_df[(tl_df['fund_year'] >= year_range[0]) & (tl_df['fund_year'] <= year_range[1])]
    if tl_sector != 'All' and 'Industry_Sector' in tl_df.columns:
        tl_df = tl_df[tl_df['Industry_Sector'] == tl_sector]
    if tl_country != 'All' and 'country_code' in tl_df.columns:
        tl_df = tl_df[tl_df['country_code'] == tl_country]
    if tl_search and 'Startup_Name' in tl_df.columns:
        tl_df = tl_df[tl_df['Startup_Name'].str.contains(tl_search, case=False, na=False)]

    tl_df = tl_df.sort_values('funded_at', ascending=False)

    st.markdown(f"**Showing {len(tl_df):,} funding events** matching filters")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Timeline visualization
    if not tl_df.empty:
        # Chart
        st.markdown('<div class="section-header">📈 Funding Volume Over Time (Filtered)</div>', unsafe_allow_html=True)
        tchart = (tl_df.dropna(subset=['raised_amount_usd'])
                 .groupby('fund_year')['raised_amount_usd']
                 .sum() / 1e9).reset_index()
        tchart.columns = ['Year', 'Funding_B']
        tchart['Year'] = tchart['Year'].astype(int)
        st.area_chart(tchart.set_index('Year'), color='#5B8DEF', height=220)

        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🗓️ Chronological Funding Events</div>', unsafe_allow_html=True)

        # Show timeline items (limit to 50 for performance)
        display_items = tl_df.head(50)
        for _, row in display_items.iterrows():
            rtype = str(row.get('funding_round_type', 'unknown'))
            dot_cls = _round_type_color(rtype)
            name   = row.get('Startup_Name', 'Unknown')
            date   = str(row.get('funded_at', ''))[:10]
            amount = row.get('raised_amount_usd', 0)
            investor = row.get('Investor_Name', 'Unknown')
            sector = row.get('Industry_Sector', 'N/A')
            country= row.get('country_code', 'N/A')

            amount_str = f"${amount/1e6:.1f}M" if pd.notna(amount) and amount > 0 else "Undisclosed"

            stage_badge_map = {
                'seed': 'badge-gold', 'seriesA': 'badge-blue',
                'seriesB': 'badge-purple', 'seriesC': 'badge-green', 'other': 'badge-rose'
            }
            badge_cls = stage_badge_map.get(dot_cls, 'badge-blue')

            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot {dot_cls}"></div>
                <div class="timeline-content">
                    <div class="timeline-title">
                        <b>{name}</b> &nbsp;
                        <span class="badge {badge_cls}">{rtype}</span>
                    </div>
                    <div class="timeline-sub">
                        📅 {date} &nbsp;|&nbsp; 💰 {amount_str} &nbsp;|&nbsp;
                        🤝 {investor} &nbsp;|&nbsp; 🏭 {sector} &nbsp;|&nbsp; 🌍 {country}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if len(tl_df) > 50:
            st.caption(f"Showing 50 of {len(tl_df):,} events. Use filters to narrow down.")

        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📋 Full Timeline Data Table</div>', unsafe_allow_html=True)
        disp = tl_df[['funded_at','Startup_Name','funding_round_type','raised_amount_usd','Investor_Name','Industry_Sector','country_code','city']].head(500)
        disp.columns = ['Date','Startup','Round Type','Amount (USD)','Investor','Sector','Country','City']
        st.dataframe(disp, use_container_width=True, height=380)
    else:
        st.info("No funding events found matching the filters.")


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 9 — INVESTOR NETWORK
# ═══════════════════════════════════════════════════════════════════════
elif page == "🤝  Investor Network":
    st.title("🤝 Investor Network & Co-Investment Intelligence")
    st.caption("PageRank-driven prestige scores, syndicate partnerships, and network centrality metrics.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Network KPIs
    n1, n2, n3, n4 = st.columns(4)
    total_investors = len(centrality_df) if not centrality_df.empty else 0
    total_edges     = len(network_df)   if not network_df.empty else 0
    max_pr  = centrality_df['PageRank_Centrality'].max() if not centrality_df.empty and 'PageRank_Centrality' in centrality_df.columns else 0
    max_deg = centrality_df['Degree'].max() if not centrality_df.empty and 'Degree' in centrality_df.columns else 0

    with n1:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value">{total_investors:,}</div>
            <div class="kpi-label">Known Investors</div>
        </div>''', unsafe_allow_html=True)
    with n2:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value purple">{total_edges:,}</div>
            <div class="kpi-label">Co-Investment Edges</div>
        </div>''', unsafe_allow_html=True)
    with n3:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value green">{max_pr:.6f}</div>
            <div class="kpi-label">Peak PageRank Score</div>
        </div>''', unsafe_allow_html=True)
    with n4:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value rose">{int(max_deg):,}</div>
            <div class="kpi-label">Highest Degree (Connections)</div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Network visualization info
    st.markdown('<div class="section-header">🕸️ Co-Investment Network Graph</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box purple">
        <b>📊 Node-Link Diagram — Co-Investment Graph</b><br>
        The interactive co-investment network graph maps investor relationships where <b>nodes = investors</b>
        and <b>edges = shared funding rounds</b>. Edge weight reflects frequency of co-investment.
        Below is the top-25 network represented via centrality metrics. For a full interactive
        graph visualization, use the <b>NetworkX + Pyvis</b> notebook (07_Investor_Network.ipynb).
    </div>
    """, unsafe_allow_html=True)

    # ── Try to show simplified network using bar charts as proxy
    if not centrality_df.empty:
        net1, net2 = st.columns(2)
        with net1:
            st.markdown("**Top 20 Investors by Network Degree (Connections)**")
            if 'Degree' in centrality_df.columns and 'Investor_Name' in centrality_df.columns:
                top20_deg = centrality_df.nlargest(20, 'Degree').set_index('Investor_Name')['Degree']
                st.bar_chart(top20_deg, color='#5B8DEF', height=300)
        with net2:
            st.markdown("**Top 20 Investors by PageRank Centrality**")
            if 'PageRank_Centrality' in centrality_df.columns and 'Investor_Name' in centrality_df.columns:
                top20_pr = centrality_df.nlargest(20, 'PageRank_Centrality').set_index('Investor_Name')['PageRank_Centrality']
                st.bar_chart(top20_pr, color='#8E5BEF', height=300)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">🏆 Top 25 Investors by PageRank Centrality</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box">
        <b>What is PageRank?</b> Borrowed from Google's algorithm — an investor's score rises when
        they co-invest with other high-PageRank investors. Higher score = more network prestige & influence.
        </div>
        """, unsafe_allow_html=True)
        if not centrality_df.empty:
            _cent_priority_cols = ['Investor_Name', 'PageRank_Centrality', 'Degree',
                                   'Degree_Centrality', 'Betweenness_Centrality']
            _cent_cols = [c for c in _cent_priority_cols if c in centrality_df.columns]
            top_investors = centrality_df.head(25)[_cent_cols].copy()
            if 'PageRank_Centrality'   in top_investors.columns: top_investors['PageRank_Centrality']   = top_investors['PageRank_Centrality'].apply(lambda x: f'{x:.8f}')
            if 'Degree_Centrality'     in top_investors.columns: top_investors['Degree_Centrality']     = top_investors['Degree_Centrality'].apply(lambda x: f'{x:.6f}')
            if 'Betweenness_Centrality'in top_investors.columns: top_investors['Betweenness_Centrality']= top_investors['Betweenness_Centrality'].apply(lambda x: f'{x:.6f}')
            top_investors.index = range(1, len(top_investors) + 1)
            st.dataframe(top_investors.rename(columns={
                'Investor_Name': 'Investor', 'Degree': 'Total Connections',
                'Degree_Centrality': 'Degree Centrality', 'Betweenness_Centrality': 'Betweenness'
            }), use_container_width=True, height=500)
        else:
            st.warning("Investor centrality data not found. Run notebook 04 first.")

    with col_r:
        st.markdown('<div class="section-header">🔗 Top 25 Strongest Co-Investment Syndicates</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box purple">
        <b>What are Syndicates?</b> Syndicates form when investors repeatedly co-invest in the same
        funding rounds. Higher weight = stronger, more frequent partnership.
        </div>
        """, unsafe_allow_html=True)
        if not network_df.empty:
            top_links = network_df.sort_values('Weight', ascending=False).head(25).reset_index(drop=True)
            top_links.index = range(1, len(top_links) + 1)
            st.dataframe(top_links, use_container_width=True, height=500)
        else:
            st.warning("Investor network data not found. Run notebook 04 first.")

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if not centrality_df.empty:
        st.markdown('<div class="section-header">📈 Investor Degree Distribution (Connections)</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            if 'Degree' in centrality_df.columns:
                _deg_series = centrality_df['Degree'].clip(upper=centrality_df['Degree'].quantile(0.99)).dropna()
                _deg_binned = pd.cut(_deg_series, bins=20)
                _deg_counts = _deg_binned.value_counts().sort_index()
                _deg_counts.index = [f'{int(i.left)}–{int(i.right)}' for i in _deg_counts.index]
                st.bar_chart(_deg_counts, color='#8E5BEF', height=240)
                st.caption("Co-investment connections per investor (clipped at P99)")
        with col4:
            if 'PageRank_Centrality' in centrality_df.columns:
                _pr_series = centrality_df['PageRank_Centrality'].dropna()
                _pr_binned = pd.cut(_pr_series, bins=20)
                _pr_counts = _pr_binned.value_counts().sort_index()
                _pr_counts.index = [f'{i.left:.5f}–{i.right:.5f}' for i in _pr_counts.index]
                st.bar_chart(_pr_counts, color='#5B8DEF', height=240)
                st.caption("PageRank centrality score distribution across all investors")

        st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔎 Investor Lookup Tool</div>', unsafe_allow_html=True)
        search_name = st.text_input("Search investor by name:", placeholder="e.g. Sequoia Capital, Andreessen Horowitz...")
        if search_name:
            results = centrality_df[centrality_df['Investor_Name'].str.contains(search_name, case=False, na=False)]
            if not results.empty:
                st.dataframe(results.reset_index(drop=True), use_container_width=True)
            else:
                st.info(f"No investors found matching '{search_name}'")


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 10 — PREDICTIVE ML ENGINE  (Startup Success & Funding Simulator)
# ═══════════════════════════════════════════════════════════════════════
elif page == "🔮  Predictive ML Engine":

    # ── Extra CSS for simulator-specific components
    st.markdown("""
    <style>
    /* Simulator result card — dynamic border glow */
    .sim-card-green {
        background: linear-gradient(135deg, #041a0f 0%, #061510 100%);
        border: 1.5px solid #22c55e;
        border-radius: 18px;
        padding: 28px 24px;
        text-align: center;
        box-shadow: 0 0 32px rgba(34,197,94,0.18);
        transition: box-shadow 0.3s ease;
    }
    .sim-card-orange {
        background: linear-gradient(135deg, #1a0f00 0%, #140d02 100%);
        border: 1.5px solid #f59e0b;
        border-radius: 18px;
        padding: 28px 24px;
        text-align: center;
        box-shadow: 0 0 32px rgba(245,158,11,0.18);
        transition: box-shadow 0.3s ease;
    }
    .sim-card-red {
        background: linear-gradient(135deg, #1a0407 0%, #140205 100%);
        border: 1.5px solid #ef4444;
        border-radius: 18px;
        padding: 28px 24px;
        text-align: center;
        box-shadow: 0 0 32px rgba(239,68,68,0.18);
        transition: box-shadow 0.3s ease;
    }
    .sim-prob-value { font-size: 3.2rem; font-weight: 900; letter-spacing: -0.03em; line-height: 1.0; }
    .sim-verdict    { font-size: 1.0rem; font-weight: 700; margin-bottom: 10px; }
    .sim-subtitle   { font-size: 0.82rem; color: #7070a8; margin-top: 8px; }
    .sandbox-row {
        background: #0e0e28;
        border: 1px solid #1e1e42;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 6px 0;
        font-size: 0.84rem;
        color: #c0c0e0;
    }
    .live-badge {
        display: inline-block;
        background: rgba(34,197,94,0.15);
        color: #22c55e;
        border: 1px solid rgba(34,197,94,0.35);
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-left: 10px;
        vertical-align: middle;
        animation: pulse-live 2s ease-in-out infinite;
    }
    @keyframes pulse-live {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.55; }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h1 style='margin-bottom:2px;'>🔮 Startup Success &amp; Funding Simulator
        <span class='live-badge'>● LIVE</span>
    </h1>
    <p style='color:#6868a0; font-size:0.9rem; margin-top:4px;'>
        Real-time AI prediction engine · Instant inference · What-If scenario analysis · Comparison sandbox
    </p>
    """, unsafe_allow_html=True)
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if success_model is None or funding_model is None:
        st.error("⚠️ Trained models not found in `models/` directory. Run notebooks 05 & 06 first.")
        st.info("Pipeline: **04_Feature_Engineering** → **05_Machine_Learning** → **06_Forecasting**")
        st.stop()

    # ── Model status strip
    n_feats_s = len(success_model.feature_names_in_) if hasattr(success_model, 'feature_names_in_') else '—'
    n_feats_f = len(funding_model.feature_names_in_) if hasattr(funding_model, 'feature_names_in_') else '—'
    ml1, ml2, ml3, ml4 = st.columns(4)
    with ml1:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value" style="font-size:1.25rem;">XGBoost</div>
            <div class="kpi-label">Classifier Architecture</div>
        </div>''', unsafe_allow_html=True)
    with ml2:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value purple" style="font-size:1.25rem;">{n_feats_s}</div>
            <div class="kpi-label">Success Model Features</div>
        </div>''', unsafe_allow_html=True)
    with ml3:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value green" style="font-size:1.25rem;">{n_feats_f}</div>
            <div class="kpi-label">Funding Model Features</div>
        </div>''', unsafe_allow_html=True)
    with ml4:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value gold" style="font-size:1.25rem;">Real-Time</div>
            <div class="kpi-label">Inference Mode</div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SHARED INFERENCE HELPER  (called instantly on every widget change)
    # ══════════════════════════════════════════════════════════════════
    def _compute_investor_pagerank(investors_list):
        """Return (max_pr, sum_pr, num_investors) with graceful fallback to medians."""
        num_inv = max(len(investors_list), 1)
        if investors_list and not centrality_df.empty:
            median_pr  = centrality_df['PageRank_Centrality'].median()
            pagers = []
            for inv in investors_list:
                score = centrality_df[centrality_df['Investor_Name'] == inv]['PageRank_Centrality'].values
                pagers.append(float(score[0]) if len(score) > 0 else median_pr)
            return max(pagers), sum(pagers), num_inv
        elif not centrality_df.empty:
            # No investors selected — use median as safe default (edge-case handled)
            med = centrality_df['PageRank_Centrality'].median()
            return med, med, 1
        return 0.0, 0.0, 1

    def _build_input_row(feature_list, base_dict, sector, country):
        """Construct a single-row DataFrame for model inference."""
        row = dict(base_dict)
        for col in feature_list:
            if col.startswith('country_code_cleaned_'):
                row[col] = [1 if col.replace('country_code_cleaned_', '') == country else 0]
            elif col.startswith('Industry_Sector_cleaned_'):
                row[col] = [1 if col.replace('Industry_Sector_cleaned_', '') == sector else 0]
            elif col not in row:
                row[col] = [0]
        return pd.DataFrame(row)[feature_list]

    def _run_inference(sector, country, n_rounds, company_age, raised_usd, recession_v, techboom_v, investors):
        """Core inference — returns (success_pred, success_prob, funding_pred_usd, funding_pred_log)."""
        max_pr, sum_pr, num_inv = _compute_investor_pagerank(investors)
        log_fund = np.log1p(raised_usd)

        base_s = {
            'Total_Funding_Rounds':    [n_rounds],
            'Unique_Investors_Count':  [num_inv],
            'Fought_Through_Recession':[recession_v],
            'Age_at_Latest_Round':     [company_age],
            'Log_Total_Funding':       [log_fund],
            'Max_Investor_PageRank':   [max_pr],
            'Sum_Investor_PageRank':   [sum_pr],
            'Funded_During_Tech_Boom': [techboom_v],
        }
        base_f = {
            'Total_Funding_Rounds':    [n_rounds],
            'Unique_Investors_Count':  [num_inv],
            'Fought_Through_Recession':[recession_v],
            'Age_at_Latest_Round':     [company_age],
            'Max_Investor_PageRank':   [max_pr],
            'Sum_Investor_PageRank':   [sum_pr],
            'Funded_During_Tech_Boom': [techboom_v],
        }
        in_s = _build_input_row(success_model.feature_names_in_, base_s, sector, country)
        in_f = _build_input_row(funding_model.feature_names_in_, base_f, sector, country)

        s_pred    = success_model.predict(in_s)[0]
        s_prob    = float(success_model.predict_proba(in_s)[0][1])
        f_log     = float(funding_model.predict(in_f)[0])
        f_usd     = float(np.expm1(f_log))
        return int(s_pred), s_prob, f_usd, f_log

    # ══════════════════════════════════════════════════════════════════
    #  SECTION A — INPUT CONFIGURATION (left) + LIVE RESULTS (right)
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">⚙️ Real-Time Configuration Panel</div>', unsafe_allow_html=True)

    cfg_col, res_col = st.columns([1.05, 0.95], gap="large")

    with cfg_col:
        st.markdown("<p style='color:#6868a0;font-size:0.82rem;'>Adjust any parameter — predictions update instantly.</p>", unsafe_allow_html=True)

        if not df.empty and 'Industry_Sector_cleaned' in df.columns:
            sectors = sorted(df['Industry_Sector_cleaned'].dropna().unique().tolist())
            default_idx = sectors.index('software') if 'software' in sectors else 0
            selected_sector = st.selectbox("🏭 Industry Sector", sectors, index=default_idx, key="sim_sector")
        else:
            selected_sector = st.text_input("Industry Sector", value="software", key="sim_sector")

        if not df.empty and 'country_code_cleaned' in df.columns:
            countries = sorted(df['country_code_cleaned'].dropna().unique().tolist())
            default_cidx = countries.index('USA') if 'USA' in countries else 0
            selected_country = st.selectbox("🌍 Country Code", countries, index=default_cidx, key="sim_country")
        else:
            selected_country = st.text_input("Country Code", value="USA", key="sim_country")

        if not centrality_df.empty:
            known_investors = sorted(centrality_df['Investor_Name'].dropna().tolist())
            selected_investors = st.multiselect(
                "🤝 Select Investor(s)",
                known_investors,
                placeholder="Leave empty to use median PageRank (default fallback)...",
                key="sim_investors"
            )
        else:
            selected_investors = []
            st.info("ℹ️ Centrality data unavailable — investor PageRank defaults to dataset median.")

        cfg_r1, cfg_r2 = st.columns(2)
        with cfg_r1:
            rounds   = st.slider("🔄 Funding Rounds", 1, 20, 3, key="sim_rounds")
            age      = st.slider("📅 Company Age (yrs)", 1, 25, 4, key="sim_age")
        with cfg_r2:
            recession_str = st.radio("📉 Recession Era (2008–09)?", ["No", "Yes"], horizontal=True, key="sim_recession")
            recession_val = 1 if recession_str == "Yes" else 0
            techboom_str  = st.radio("🚀 Tech Boom (2014–21)?", ["No", "Yes"], horizontal=True, key="sim_techboom")
            tech_boom_val = 1 if techboom_str == "Yes" else 0

        funding_raised = st.number_input(
            "💰 Total Funding Raised So Far (USD)",
            min_value=0, value=5_000_000, step=500_000,
            help="Cumulative capital raised to date — used as a feature for success prediction.",
            key="sim_funding"
        )
        log_funding_val = np.log1p(funding_raised)

    # ── Run real-time inference (no button required)
    with res_col:
        success_pred, success_prob, funding_pred_usd, funding_pred_log = _run_inference(
            selected_sector, selected_country,
            rounds, age, funding_raised,
            recession_val, tech_boom_val,
            selected_investors
        )

        # Dynamic colour theme based on probability
        prob_pct = success_prob * 100
        if prob_pct >= 60:
            card_cls   = "sim-card-green"
            prob_color = "#22c55e"
            verdict    = "✅ Strong Exit Signal"
            tier_badge = "🟢 HIGH CONFIDENCE"
        elif prob_pct >= 40:
            card_cls   = "sim-card-orange"
            prob_color = "#f59e0b"
            verdict    = "⚡ Moderate Exit Potential"
            tier_badge = "🟡 MODERATE"
        else:
            card_cls   = "sim-card-red"
            prob_color = "#ef4444"
            verdict    = "⚠️ Low Exit Likelihood"
            tier_badge = "🔴 LOW CONFIDENCE"

        st.markdown("<br>", unsafe_allow_html=True)
        max_pr_val, sum_pr, num_investors = _compute_investor_pagerank(selected_investors)

        # ── Main result card
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="sim-verdict" style="color:{prob_color};">{verdict}</div>
            <div class="sim-prob-value" style="color:{prob_color};">{prob_pct:.1f}%</div>
            <div class="sim-subtitle">Exit Success Probability (Acquisition or IPO)</div>
            <div style="margin-top:14px;">
                <span class="badge badge-blue" style="font-size:0.7rem;">{tier_badge}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Funding prediction card
        st.markdown(f"""
        <div class="kpi-card" style="text-align:left; padding:18px 22px;">
            <div style="font-size:0.72rem; color:#6868a0; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:6px;">💡 Predicted Lifetime Funding</div>
            <div style="font-size:1.9rem; font-weight:800; color:#8E5BEF; letter-spacing:-0.02em;">${funding_pred_usd:,.0f}</div>
            <div style="font-size:0.78rem; color:#4a4a80; margin-top:4px;">Log scale: {funding_pred_log:.3f} &nbsp;|&nbsp; Input raised: ${funding_raised:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Probability gauge bar
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.8rem; color:#6060a0; margin-bottom:4px;'>Exit Probability Gauge</p>", unsafe_allow_html=True)
        st.progress(float(success_prob))

        # ── Insight chips
        ins_a, ins_b = st.columns(2)
        with ins_a:
            st.markdown(f"""
            <div class="insight-box" style="margin:0;">
                <b style="font-size:0.8rem;">📊 Investor Signal</b><br>
                Max PageRank: <code>{max_pr_val:.6f}</code><br>
                Sum PageRank: <code>{sum_pr:.6f}</code><br>
                Investors: <code>{num_investors}</code>
            </div>""", unsafe_allow_html=True)
        with ins_b:
            st.markdown(f"""
            <div class="insight-box purple" style="margin:0;">
                <b style="font-size:0.8rem;">🌍 Profile Snapshot</b><br>
                Sector: <code>{selected_sector}</code><br>
                Country: <code>{selected_country}</code><br>
                Age: <code>{age} yrs</code> &nbsp; Rounds: <code>{rounds}</code>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION B — WHAT-IF SENSITIVITY ANALYSIS (interactive Plotly chart)
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">📈 What-If Sensitivity Analysis — Funding vs. Exit Probability</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6868a0;font-size:0.83rem;'>This chart sweeps <b>Total Funding Raised</b> from $0 to 5× your current input "
        "while holding all other parameters constant — revealing how capital alone shifts your exit odds.</p>",
        unsafe_allow_html=True
    )

    # Compute sensitivity curve
    max_funding_range = max(funding_raised * 5, 50_000_000)  # at least $50M range
    funding_sweep     = np.linspace(0, max_funding_range, 60)
    prob_sweep        = []
    for f_val in funding_sweep:
        _, sp, _, _ = _run_inference(
            selected_sector, selected_country,
            rounds, age, float(f_val),
            recession_val, tech_boom_val,
            selected_investors
        )
        prob_sweep.append(sp * 100)

    fig_whatif = go.Figure()

    # Gradient fill under curve
    fig_whatif.add_trace(go.Scatter(
        x=funding_sweep / 1e6,
        y=prob_sweep,
        mode='lines',
        name='Exit Probability',
        line=dict(color='#5B8DEF', width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(91,141,239,0.10)',
        hovertemplate='<b>Funding: $%{x:.1f}M</b><br>Exit Prob: %{y:.1f}%<extra></extra>'
    ))

    # 60% threshold line
    fig_whatif.add_hline(
        y=60, line_dash='dash', line_color='rgba(34,197,94,0.5)', line_width=1.2,
        annotation_text='60% threshold (High Confidence)', annotation_position='top left',
        annotation_font=dict(color='#22c55e', size=11)
    )
    # 40% threshold line
    fig_whatif.add_hline(
        y=40, line_dash='dash', line_color='rgba(245,158,11,0.5)', line_width=1.2,
        annotation_text='40% threshold (Moderate)', annotation_position='top left',
        annotation_font=dict(color='#f59e0b', size=11)
    )

    # Current configuration marker
    fig_whatif.add_trace(go.Scatter(
        x=[funding_raised / 1e6],
        y=[prob_pct],
        mode='markers+text',
        name='Your Configuration',
        marker=dict(size=14, color=prob_color, symbol='circle',
                    line=dict(color='white', width=2)),
        text=[f' {prob_pct:.1f}%'],
        textposition='middle right',
        textfont=dict(color=prob_color, size=12, family='Inter'),
        hovertemplate=f'<b>Current Config</b><br>Funding: ${funding_raised/1e6:.1f}M<br>Exit Prob: {prob_pct:.1f}%<extra></extra>'
    ))

    fig_whatif.update_layout(
        paper_bgcolor='#07071a',
        plot_bgcolor='#0a0a20',
        font=dict(family='Inter', color='#c0c0e0'),
        height=380,
        margin=dict(l=60, r=30, t=30, b=50),
        xaxis=dict(
            title='Total Funding Raised (USD Millions)',
            title_font=dict(size=12, color='#7070a8'),
            tickfont=dict(size=11, color='#7070a8'),
            gridcolor='#161636',
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title='Exit Success Probability (%)',
            title_font=dict(size=12, color='#7070a8'),
            tickfont=dict(size=11, color='#7070a8'),
            gridcolor='#161636',
            showgrid=True,
            zeroline=False,
            range=[0, 105],
        ),
        legend=dict(
            bgcolor='rgba(10,10,32,0.8)',
            bordercolor='#1e1e40',
            borderwidth=1,
            font=dict(size=11)
        ),
        hovermode='x unified',
    )
    st.plotly_chart(fig_whatif, use_container_width=True)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION C — STARTUP COMPARISON SANDBOX
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">🧪 Startup Comparison Sandbox</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6868a0;font-size:0.83rem;'>Save the current startup configuration to compare multiple profiles side-by-side. "
        "Build your own benchmark dataset interactively.</p>",
        unsafe_allow_html=True
    )

    # Initialise session-state list
    if 'sandbox_configs' not in st.session_state:
        st.session_state['sandbox_configs'] = []

    sand_btn1, sand_btn2, _ = st.columns([1, 1, 4])
    with sand_btn1:
        if st.button("💾 Save Current Configuration", use_container_width=True):
            entry = {
                'Label':          f"Config #{len(st.session_state['sandbox_configs']) + 1}",
                'Sector':         selected_sector,
                'Country':        selected_country,
                'Rounds':         rounds,
                'Age (yrs)':      age,
                'Raised ($M)':    round(funding_raised / 1e6, 2),
                'Recession Era':  recession_str,
                'Tech Boom':      techboom_str,
                'Investors':      len(selected_investors),
                'Exit Prob (%)':  round(prob_pct, 1),
                'Pred Funding ($)': round(funding_pred_usd, 0),
            }
            st.session_state['sandbox_configs'].append(entry)
            st.success(f"✅ Saved as **{entry['Label']}**")

    with sand_btn2:
        if st.button("🗑️ Clear Sandbox", use_container_width=True):
            st.session_state['sandbox_configs'] = []
            st.info("Sandbox cleared.")

    saved = st.session_state['sandbox_configs']

    if saved:
        st.markdown("<br>", unsafe_allow_html=True)
        sandbox_df = pd.DataFrame(saved)

        # ── Comparison table
        st.markdown('<div class="section-header" style="font-size:0.9rem;">📋 Saved Configurations</div>', unsafe_allow_html=True)
        display_cols = ['Label', 'Sector', 'Country', 'Rounds', 'Age (yrs)', 'Raised ($M)', 'Exit Prob (%)', 'Pred Funding ($)']
        st.dataframe(
            sandbox_df[display_cols].style
                .background_gradient(subset=['Exit Prob (%)'], cmap='RdYlGn', vmin=0, vmax=100)
                .format({'Raised ($M)': '{:.2f}', 'Exit Prob (%)': '{:.1f}', 'Pred Funding ($)': '${:,.0f}'}),
            use_container_width=True,
            height=min(60 + len(saved) * 40, 380)
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Comparison bar charts (Exit Prob + Predicted Funding)
        cmp1, cmp2 = st.columns(2)
        with cmp1:
            st.markdown('<div class="section-header" style="font-size:0.88rem;">📊 Exit Success Probability (%)</div>', unsafe_allow_html=True)
            bar_colors_prob = [
                '#22c55e' if v >= 60 else ('#f59e0b' if v >= 40 else '#ef4444')
                for v in sandbox_df['Exit Prob (%)']
            ]
            fig_cmp1 = go.Figure(go.Bar(
                x=sandbox_df['Label'],
                y=sandbox_df['Exit Prob (%)'],
                marker_color=bar_colors_prob,
                text=[f"{v:.1f}%" for v in sandbox_df['Exit Prob (%)']],
                textposition='outside',
                textfont=dict(size=11, color='#c0c0e0'),
                hovertemplate='<b>%{x}</b><br>Exit Prob: %{y:.1f}%<extra></extra>'
            ))
            fig_cmp1.update_layout(
                paper_bgcolor='#07071a', plot_bgcolor='#0a0a20',
                font=dict(family='Inter', color='#c0c0e0'),
                height=260, margin=dict(l=20, r=20, t=20, b=40),
                yaxis=dict(range=[0, 110], gridcolor='#161636', ticksuffix='%', tickfont=dict(size=10)),
                xaxis=dict(tickfont=dict(size=10)),
                showlegend=False,
            )
            st.plotly_chart(fig_cmp1, use_container_width=True)

        with cmp2:
            st.markdown('<div class="section-header" style="font-size:0.88rem;">💰 Predicted Lifetime Funding (USD)</div>', unsafe_allow_html=True)
            fig_cmp2 = go.Figure(go.Bar(
                x=sandbox_df['Label'],
                y=sandbox_df['Pred Funding ($)'] / 1e6,
                marker_color='#8E5BEF',
                marker_opacity=0.85,
                text=[f"${v/1e6:.1f}M" for v in sandbox_df['Pred Funding ($)']],
                textposition='outside',
                textfont=dict(size=11, color='#c0c0e0'),
                hovertemplate='<b>%{x}</b><br>Pred Funding: $%{y:.1f}M<extra></extra>'
            ))
            fig_cmp2.update_layout(
                paper_bgcolor='#07071a', plot_bgcolor='#0a0a20',
                font=dict(family='Inter', color='#c0c0e0'),
                height=260, margin=dict(l=20, r=20, t=20, b=40),
                yaxis=dict(gridcolor='#161636', tickprefix='$', ticksuffix='M', tickfont=dict(size=10)),
                xaxis=dict(tickfont=dict(size=10)),
                showlegend=False,
            )
            st.plotly_chart(fig_cmp2, use_container_width=True)

    else:
        st.markdown("""
        <div style='background:#0a0a20; border:1px dashed #2a2a50; border-radius:14px; padding:32px;
                    text-align:center; color:#4a4a80; font-size:0.88rem;'>
            📂 No configurations saved yet.<br>
            <span style='font-size:0.80rem;'>Configure your startup above and click <b>💾 Save Current Configuration</b> to start comparing.</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION D — PDF REPORT GENERATOR
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">📄 PDF Report Generator</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6868a0;font-size:0.83rem;'>Download a professional prediction report for the <b>current real-time configuration</b>.</p>",
        unsafe_allow_html=True
    )

    def generate_prediction_pdf(
        sector, country, n_rounds, company_age, raised_usd,
        recession_s, techboom_s, n_inv_selected,
        s_prob, f_usd, f_log,
        max_pr, sum_pr_val, n_inv_used,
        funding_sweep_x, prob_sweep_y, current_funding_m, current_prob
    ):
        """
        Build a matplotlib-based PDF report for the current prediction configuration.
        Returns bytes of the rendered PDF.
        """
        fig = plt.figure(figsize=(10, 14), facecolor='#07071a')
        fig.patch.set_facecolor('#07071a')

        # ── Title block
        fig.text(0.08, 0.96, '🔮 Startup Success & Funding Prediction Report',
                 fontsize=16, fontweight='bold', color='#e0e0f0', va='top')
        fig.text(0.08, 0.935, 'Generated by Ledger — Startup Intelligence Platform',
                 fontsize=9, color='#5060a0', va='top')

        # horizontal rule (line)
        line = plt.Line2D([0.06, 0.94], [0.92, 0.92], transform=fig.transFigure,
                          color='#2c2c58', linewidth=1)
        fig.add_artist(line)

        # ── Section: Configuration
        fig.text(0.08, 0.905, 'STARTUP PROFILE', fontsize=9, fontweight='bold',
                 color='#5B8DEF', va='top')
        cfg_lines = [
            f"Industry Sector   :  {sector}",
            f"Country Code      :  {country}",
            f"Funding Rounds    :  {n_rounds}",
            f"Company Age       :  {company_age} yrs",
            f"Total Raised      :  ${raised_usd:,.0f}",
            f"Recession Era     :  {recession_s}",
            f"Tech Boom Period  :  {techboom_s}",
            f"Investors Selected:  {n_inv_selected} (used: {n_inv_used})",
        ]
        for i, line_txt in enumerate(cfg_lines):
            fig.text(0.08, 0.882 - i * 0.025, line_txt, fontsize=9,
                     color='#c0c0e0', va='top', fontfamily='monospace')

        line2 = plt.Line2D([0.06, 0.94], [0.665, 0.665], transform=fig.transFigure,
                           color='#2c2c58', linewidth=1)
        fig.add_artist(line2)

        # ── Section: Predictions
        prob_pct_r = s_prob * 100
        if prob_pct_r >= 60:
            result_color = '#22c55e'
            verdict_txt  = 'STRONG EXIT SIGNAL'
        elif prob_pct_r >= 40:
            result_color = '#f59e0b'
            verdict_txt  = 'MODERATE EXIT POTENTIAL'
        else:
            result_color = '#ef4444'
            verdict_txt  = 'LOW EXIT LIKELIHOOD'

        fig.text(0.08, 0.648, 'PREDICTION RESULTS', fontsize=9, fontweight='bold',
                 color='#5B8DEF', va='top')
        fig.text(0.08, 0.620, f'Exit Success Probability:  {prob_pct_r:.1f}%',
                 fontsize=18, fontweight='bold', color=result_color, va='top')
        fig.text(0.08, 0.587, verdict_txt,
                 fontsize=10, fontweight='bold', color=result_color, va='top')
        fig.text(0.08, 0.562, f'Predicted Lifetime Funding:  ${f_usd:,.0f}',
                 fontsize=12, color='#8E5BEF', va='top')
        fig.text(0.08, 0.540, f'Log-scale funding value:      {f_log:.4f}',
                 fontsize=9, color='#6060a0', va='top', fontfamily='monospace')
        fig.text(0.08, 0.518, f'Investor Max PageRank:        {max_pr:.8f}',
                 fontsize=9, color='#6060a0', va='top', fontfamily='monospace')
        fig.text(0.08, 0.500, f'Investor Sum PageRank:        {sum_pr_val:.8f}',
                 fontsize=9, color='#6060a0', va='top', fontfamily='monospace')

        line3 = plt.Line2D([0.06, 0.94], [0.485, 0.485], transform=fig.transFigure,
                           color='#2c2c58', linewidth=1)
        fig.add_artist(line3)

        # ── What-If chart embedded in PDF
        ax = fig.add_axes([0.08, 0.15, 0.84, 0.30])
        ax.set_facecolor('#0a0a20')
        ax.plot(funding_sweep_x, prob_sweep_y, color='#5B8DEF', linewidth=2)
        ax.fill_between(funding_sweep_x, prob_sweep_y, alpha=0.12, color='#5B8DEF')
        ax.axhline(60, color='#22c55e', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.axhline(40, color='#f59e0b', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.scatter([current_funding_m], [current_prob], color=result_color, s=80, zorder=5)
        ax.set_xlabel('Total Funding Raised ($M)', color='#7070a8', fontsize=9)
        ax.set_ylabel('Exit Success Probability (%)', color='#7070a8', fontsize=9)
        ax.set_title('What-If Sensitivity: Funding vs. Exit Probability', color='#c0c0e0', fontsize=10)
        ax.tick_params(colors='#7070a8', labelsize=8)
        ax.spines['bottom'].set_color('#2c2c58')
        ax.spines['left'].set_color('#2c2c58')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, color='#161636', linewidth=0.5)
        ax.set_ylim(0, 105)

        # ── Footer
        fig.text(0.08, 0.06, 'Ledger · Startup Intelligence Platform · Leakage-Free Model Architecture',
                 fontsize=8, color='#3a3a60', va='top')
        fig.text(0.08, 0.045, 'This report was generated automatically. Predictions are probabilistic and not financial advice.',
                 fontsize=7.5, color='#3a3a60', va='top')

        buf = io.BytesIO()
        plt.savefig(buf, format='pdf', facecolor='#07071a', bbox_inches='tight', dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    pdf_c1, pdf_c2 = st.columns([2, 3])
    with pdf_c1:
        pdf_bytes = generate_prediction_pdf(
            sector=selected_sector,
            country=selected_country,
            n_rounds=rounds,
            company_age=age,
            raised_usd=funding_raised,
            recession_s=recession_str,
            techboom_s=techboom_str,
            n_inv_selected=len(selected_investors),
            s_prob=success_prob,
            f_usd=funding_pred_usd,
            f_log=funding_pred_log,
            max_pr=max_pr_val,
            sum_pr_val=sum_pr,
            n_inv_used=num_investors,
            funding_sweep_x=[v / 1e6 for v in funding_sweep],
            prob_sweep_y=prob_sweep,
            current_funding_m=funding_raised / 1e6,
            current_prob=prob_pct
        )
        st.download_button(
            label="📥 Download Prediction Report (PDF)",
            data=pdf_bytes,
            file_name=f"startup_prediction_{selected_sector}_{selected_country}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with pdf_c2:
        st.markdown(f"""
        <div class="insight-box" style="margin:0;">
            <b>📋 Report Contents</b><br>
            ✦ Full startup configuration profile<br>
            ✦ Exit success probability: <b style='color:{prob_color};'>{prob_pct:.1f}%</b><br>
            ✦ Predicted lifetime funding: <b style='color:#8E5BEF;'>${funding_pred_usd:,.0f}</b><br>
            ✦ Investor PageRank signals<br>
            ✦ What-If sensitivity chart (embedded)
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 11 — REPORTS & EXPORT  (NEW)
# ═══════════════════════════════════════════════════════════════════════
elif page == "📊  Reports & Export":
    st.title("📊 Reports & Export Center")
    st.caption("Centralized interface to filter metrics and export custom reports for stakeholders.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found.")
        st.stop()

    st.markdown('<div class="section-header">📋 Report Configuration</div>', unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns(3)

    with rc1:
        rep_sectors = st.multiselect(
            "Filter Sectors",
            sorted(df['Industry_Sector_cleaned'].dropna().unique().tolist()) if 'Industry_Sector_cleaned' in df.columns else [],
            placeholder="All sectors"
        )
    with rc2:
        rep_countries = st.multiselect(
            "Filter Countries",
            sorted(df['country_code_cleaned'].dropna().unique().tolist()) if 'country_code_cleaned' in df.columns else [],
            placeholder="All countries"
        )
    with rc3:
        rep_status = st.selectbox("Exit Status", ['All', 'Successful', 'Not Exited'])

    # Apply
    rep_df = df.copy()
    if rep_sectors and 'Industry_Sector_cleaned' in rep_df.columns:
        rep_df = rep_df[rep_df['Industry_Sector_cleaned'].isin(rep_sectors)]
    if rep_countries and 'country_code_cleaned' in rep_df.columns:
        rep_df = rep_df[rep_df['country_code_cleaned'].isin(rep_countries)]
    if rep_status == 'Successful' and 'is_successful' in rep_df.columns:
        rep_df = rep_df[rep_df['is_successful'] == 1]
    elif rep_status == 'Not Exited' and 'is_successful' in rep_df.columns:
        rep_df = rep_df[rep_df['is_successful'] == 0]

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Summary metrics
    st.markdown('<div class="section-header">📈 Report Summary Metrics</div>', unsafe_allow_html=True)

    _co  = rep_df['company_id'].nunique() if 'company_id' in rep_df.columns else len(rep_df)
    _cap = rep_df['Total_Funding_USD'].sum()/1e9 if ('Total_Funding_USD' in rep_df.columns and not rep_df.empty) else 0
    _hi  = rep_df['Total_Funding_USD'].max()/1e6 if ('Total_Funding_USD' in rep_df.columns and not rep_df.empty) else 0
    _avg = rep_df['Total_Funding_USD'].mean()/1e6 if ('Total_Funding_USD' in rep_df.columns and not rep_df.empty) else 0
    _sr  = rep_df['is_successful'].mean()*100 if ('is_successful' in rep_df.columns and not rep_df.empty) else 0
    _ar  = rep_df['Total_Funding_Rounds'].mean() if ('Total_Funding_Rounds' in rep_df.columns and not rep_df.empty) else 0

    rma, rmb, rmc = st.columns(3)
    with rma:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value" style="font-size:1.4rem;">{_co:,}</div>
            <div class="kpi-label">Companies</div></div>''', unsafe_allow_html=True)
    with rmb:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value green" style="font-size:1.4rem;">${_cap:.2f}B</div>
            <div class="kpi-label">Total Capital</div></div>''', unsafe_allow_html=True)
    with rmc:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value gold" style="font-size:1.4rem;">${_hi:.0f}M</div>
            <div class="kpi-label">Highest Deal</div></div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    rmd, rme, rmf = st.columns(3)
    with rmd:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value cyan" style="font-size:1.4rem;">${_avg:.1f}M</div>
            <div class="kpi-label">Avg Deal Size</div></div>''', unsafe_allow_html=True)
    with rme:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value rose" style="font-size:1.4rem;">{_sr:.1f}%</div>
            <div class="kpi-label">Success Rate</div></div>''', unsafe_allow_html=True)
    with rmf:
        st.markdown(f'''<div class="kpi-card">
            <div class="kpi-value purple" style="font-size:1.4rem;">{_ar:.1f}</div>
            <div class="kpi-label">Avg Rounds</div></div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts in report
    rch1, rch2 = st.columns(2)
    with rch1:
        st.markdown('<div class="section-header">📊 Capital by Sector</div>', unsafe_allow_html=True)
        if 'Industry_Sector_cleaned' in rep_df.columns and 'Total_Funding_USD' in rep_df.columns:
            sec_cap = (rep_df.groupby('Industry_Sector_cleaned')['Total_Funding_USD']
                      .sum() / 1e9).sort_values(ascending=False).head(10)
            st.bar_chart(sec_cap, color='#5B8DEF', height=260)
    with rch2:
        st.markdown('<div class="section-header">🌍 Capital by Country</div>', unsafe_allow_html=True)
        if 'country_code_cleaned' in rep_df.columns and 'Total_Funding_USD' in rep_df.columns:
            ctry_cap = (rep_df.groupby('country_code_cleaned')['Total_Funding_USD']
                       .sum() / 1e9).sort_values(ascending=False).head(10)
            st.bar_chart(ctry_cap, color='#8E5BEF', height=260)

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    # ── Export options
    st.markdown('<div class="section-header">⬇️ Export Report Data</div>', unsafe_allow_html=True)
    exp1, exp2, exp3 = st.columns(3)

    # CSV export
    with exp1:
        st.markdown("**📄 CSV Export**")
        csv_data = rep_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="startup_funding_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Sector summary CSV
    with exp2:
        st.markdown("**📊 Sector Summary**")
        if 'Industry_Sector_cleaned' in rep_df.columns:
            sec_summary = rep_df.groupby('Industry_Sector_cleaned').agg(
                Companies=('company_id','nunique'),
                Total_Funding_B=('Total_Funding_USD', lambda x: round(x.sum()/1e9, 3)),
                Avg_Funding_M=('Total_Funding_USD', lambda x: round(x.mean()/1e6, 2)),
                Success_Rate=('is_successful', lambda x: round(x.mean()*100, 1))
            ).reset_index().rename(columns={'Industry_Sector_cleaned':'Sector'})
            sec_csv = sec_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Sector Summary",
                data=sec_csv,
                file_name="sector_summary_report.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Country summary CSV
    with exp3:
        st.markdown("**🌍 Country Summary**")
        if 'country_code_cleaned' in rep_df.columns:
            ctry_summary = rep_df.groupby('country_code_cleaned').agg(
                Companies=('company_id','nunique'),
                Total_Funding_B=('Total_Funding_USD', lambda x: round(x.sum()/1e9, 3)),
                Success_Rate=('is_successful', lambda x: round(x.mean()*100, 1))
            ).reset_index().rename(columns={'country_code_cleaned':'Country'})
            ctry_csv = ctry_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Country Summary",
                data=ctry_csv,
                file_name="country_summary_report.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 Filtered Dataset Preview</div>', unsafe_allow_html=True)
    st.markdown(f"**{len(rep_df):,} companies** match your filter criteria")
    preview_cols = [c for c in ['Startup_Name','Industry_Sector_cleaned','country_code_cleaned','city',
                               'Total_Funding_USD','Total_Funding_Rounds','Unique_Investors_Count','is_successful']
                   if c in rep_df.columns]
    st.dataframe(rep_df[preview_cols].head(300), use_container_width=True, height=380)


# ═══════════════════════════════════════════════════════════════════════
#  PAGE 12 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════════
elif page == "📋  Data Explorer":
    st.title("📋 Raw Feature Dataset Explorer")
    st.caption("Browse, filter, and inspect the complete engineered feature matrix.")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not found.")
        st.stop()

    st.markdown('<div class="section-header">🔍 Filters</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        if 'country_code_cleaned' in df.columns:
            countries = ['All'] + sorted(df['country_code_cleaned'].dropna().unique().tolist())
            sel_country = st.selectbox("Country", countries)
        else:
            sel_country = 'All'
    with f2:
        if 'Industry_Sector_cleaned' in df.columns:
            sectors = ['All'] + sorted(df['Industry_Sector_cleaned'].dropna().unique().tolist())
            sel_sector = st.selectbox("Industry Sector", sectors)
        else:
            sel_sector = 'All'
    with f3:
        if 'is_successful' in df.columns:
            sel_status = st.selectbox("Exit Status", ['All', 'Successful (1)', 'Not Successful (0)'])
        else:
            sel_status = 'All'

    filt_df = df.copy()
    if sel_country != 'All' and 'country_code_cleaned' in filt_df.columns:
        filt_df = filt_df[filt_df['country_code_cleaned'] == sel_country]
    if sel_sector != 'All' and 'Industry_Sector_cleaned' in filt_df.columns:
        filt_df = filt_df[filt_df['Industry_Sector_cleaned'] == sel_sector]
    if sel_status == 'Successful (1)' and 'is_successful' in filt_df.columns:
        filt_df = filt_df[filt_df['is_successful'] == 1]
    elif sel_status == 'Not Successful (0)' and 'is_successful' in filt_df.columns:
        filt_df = filt_df[filt_df['is_successful'] == 0]

    st.markdown(f"**Showing {len(filt_df):,} of {len(df):,} companies** after filters")
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    all_cols = filt_df.columns.tolist()
    default_cols = [c for c in [
        'company_id', 'Startup_Name', 'Industry_Sector_cleaned', 'country_code_cleaned', 'city',
        'Total_Funding_USD', 'Total_Funding_Rounds', 'Unique_Investors_Count',
        'Age_at_Latest_Round', 'Log_Total_Funding', 'Max_Investor_PageRank', 'is_successful'
    ] if c in all_cols]

    selected_cols = st.multiselect("Select columns to display:", all_cols, default=default_cols)
    if not selected_cols:
        selected_cols = default_cols

    st.markdown('<div class="section-header">📊 Summary Statistics</div>', unsafe_allow_html=True)
    numeric_summary = filt_df[selected_cols].select_dtypes(include=[np.number])
    if not numeric_summary.empty:
        st.dataframe(numeric_summary.describe().round(4), use_container_width=True, height=220)

    st.markdown('<div class="section-header">📋 Feature Matrix</div>', unsafe_allow_html=True)
    st.dataframe(filt_df[selected_cols].head(500), use_container_width=True, height=450)
    st.caption(f"Displaying up to 500 rows. Total filtered rows: {len(filt_df):,}")

    csv_data = filt_df[selected_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download Filtered Dataset (CSV)",
        data=csv_data,
        file_name="startup_funding_filtered.csv",
        mime="text/csv"
    )