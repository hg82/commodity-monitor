"""
app.py
Commodity Price Monitor / Brazil
hugotolomei.com
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from modules.prices import get_commodity_prices, get_latest_prices, COMMODITIES
from modules.exports import get_exports_by_commodity, get_annual_exports_summary
from modules.fx import get_brl_usd, get_current_rate

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Commodity Monitor | Brazil",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# STYLE
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ---- ROOT TOKENS ---- */
:root {
    --green:      #00C896;
    --green-dim:  #00C89622;
    --red:        #FF4D6D;
    --red-dim:    #FF4D6D22;
    --gold:       #C9A547;
    --gold-dim:   #C9A54720;
    --bg:         #080C10;
    --bg2:        #0D1117;
    --bg3:        #131A22;
    --border:     #1E2A36;
    --text:       #E8EDF2;
    --text-muted: #5A7080;
    --font-serif: 'DM Serif Display', Georgia, serif;
    --font-sans:  'DM Sans', system-ui, sans-serif;
    --font-mono:  'DM Mono', monospace;
}

/* ---- GLOBAL ---- */
html, body, [class*="css"] {
    font-family: var(--font-sans);
    background-color: var(--bg) !important;
    color: var(--text);
}

.main .block-container {
    padding: 2rem 2.5rem 4rem;
    max-width: 1200px;
}

/* ---- SIDEBAR ---- */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.2rem;
}

/* ---- HEADINGS ---- */
h1 {
    font-family: var(--font-serif) !important;
    font-size: 2.6rem !important;
    font-weight: 400 !important;
    letter-spacing: -0.02em !important;
    color: var(--text) !important;
    line-height: 1.1 !important;
    margin-bottom: 0.3rem !important;
}

h2 {
    font-family: var(--font-serif) !important;
    font-size: 1.5rem !important;
    font-weight: 400 !important;
    color: var(--text) !important;
    margin-top: 2rem !important;
}

h3 {
    font-family: var(--font-sans) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    margin-bottom: 1rem !important;
}

/* ---- DIVIDER ---- */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ---- METRICS ---- */
[data-testid="stMetric"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1.2rem 1.4rem !important;
    transition: border-color 0.2s;
}

[data-testid="stMetric"]:hover {
    border-color: var(--gold) !important;
}

[data-testid="stMetricLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

[data-testid="stMetricValue"] {
    font-family: var(--font-serif) !important;
    font-size: 1.8rem !important;
    color: var(--text) !important;
}

/* ---- SELECTBOX / SLIDER ---- */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSlider"] {
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* ---- RADIO (nav) ---- */
[data-testid="stRadio"] label {
    font-family: var(--font-sans) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    padding: 0.4rem 0 !important;
    transition: color 0.2s;
}

[data-testid="stRadio"] label:hover {
    color: var(--text) !important;
}

/* ---- CAPTION / FOOTNOTE ---- */
[data-testid="stCaptionContainer"] {
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    color: var(--text-muted) !important;
}

/* ---- WARNING / INFO ---- */
[data-testid="stAlert"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

/* ---- EXPANDER ---- */
[data-testid="stExpander"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* ---- DATAFRAME ---- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ---- PRICE ROW CARD ---- */
.price-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.2rem;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s, transform 0.15s;
}
.price-row:hover {
    border-color: var(--gold);
    transform: translateX(3px);
}
.price-name {
    font-family: var(--font-sans);
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text);
    min-width: 100px;
}
.price-value {
    font-family: var(--font-mono);
    font-size: 1rem;
    color: var(--text);
}
.price-unit {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-left: 4px;
}
.price-change-up {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--green);
    background: var(--green-dim);
    padding: 2px 8px;
    border-radius: 20px;
}
.price-change-down {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--red);
    background: var(--red-dim);
    padding: 2px 8px;
    border-radius: 20px;
}
.price-date {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-muted);
}

/* ---- PAGE HEADER ---- */
.page-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.4rem;
}

/* ---- RATE CARD ---- */
.rate-card {
    background: linear-gradient(135deg, var(--bg3) 0%, #0D1A10 100%);
    border: 1px solid var(--green);
    border-radius: 12px;
    padding: 1.8rem;
    text-align: center;
}
.rate-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 0.5rem;
}
.rate-value {
    font-family: var(--font-serif);
    font-size: 2.4rem;
    color: var(--text);
    line-height: 1;
}
.rate-sub {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.4rem;
}

/* ---- SIDEBAR BRAND ---- */
.sidebar-brand {
    margin-bottom: 1.5rem;
}
.sidebar-brand-title {
    font-family: var(--font-serif);
    font-size: 1.3rem;
    color: var(--text);
    line-height: 1.2;
}
.sidebar-brand-sub {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--gold);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 2px;
}
.sidebar-section-label {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.5rem 0 0.6rem;
}
.sidebar-source {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-muted);
    padding: 0.3rem 0;
    border-bottom: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# PLOTLY THEME
# --------------------------------------------------

PLOT_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#E8EDF2", size=12),
    xaxis=dict(gridcolor="#1E2A36", linecolor="#1E2A36", tickfont=dict(size=11, color="#5A7080")),
    yaxis=dict(gridcolor="#1E2A36", linecolor="#1E2A36", tickfont=dict(size=11, color="#5A7080")),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(bgcolor="#0D1117", font_size=12, bordercolor="#1E2A36"),
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">Commodity Monitor</div>
        <div class="sidebar-brand-sub">Brazil · hugotolomei.com</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "",
        ["Overview", "International Prices", "Brazil Exports", "BRL vs Commodities"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="sidebar-section-label">Data sources</div>
    <div class="sidebar-source">Yahoo Finance</div>
    <div class="sidebar-source">Comex Stat / MDIC</div>
    <div class="sidebar-source">Banco Central do Brasil</div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# PAGE 1: OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.markdown('<div class="page-eyebrow">Dashboard</div>', unsafe_allow_html=True)
    st.title("Commodity Monitor")
    st.markdown("International prices and Brazilian export data for grains and soft commodities.")
    st.divider()

    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown("### Latest Prices")
        with st.spinner(""):
            df_prices = get_latest_prices()
        if not df_prices.empty:
            for _, row in df_prices.iterrows():
                change_class = "price-change-up" if row["Change %"] >= 0 else "price-change-down"
                sign = "▲" if row["Change %"] >= 0 else "▼"
                st.markdown(f"""
                <div class="price-row">
                    <span class="price-name">{row['Commodity']}</span>
                    <span class="price-value">{row['Price']:.2f}<span class="price-unit">{row['Unit']}</span></span>
                    <span class="{change_class}">{sign} {abs(row['Change %']):.2f}%</span>
                    <span class="price-date">{row['Date']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Could not load commodity prices.")

    with col2:
        st.markdown("### Exchange Rate")
        rate = get_current_rate()
        if rate:
            st.markdown(f"""
            <div class="rate-card">
                <div class="rate-label">USD / BRL</div>
                <div class="rate-value">R$ {rate:.4f}</div>
                <div class="rate-sub">Banco Central do Brasil</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Exchange rate unavailable.")

    st.divider()
    st.markdown("### Export Summary — 2023")

    with st.spinner(""):
        df_exp = get_annual_exports_summary(year=2023)

    if not df_exp.empty:
        fig = px.bar(
            df_exp,
            x="Commodity",
            y="Exports (USD)",
            color="Commodity",
            color_discrete_sequence=["#C9A547", "#00C896", "#4FC3F7", "#FF6B6B", "#B39DDB", "#80CBC4"],
            title="Brazilian exports by commodity (2023)",
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            showlegend=False,
            title_font=dict(family="DM Serif Display", size=16, color="#E8EDF2"),
            **PLOT_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Export data is being fetched. Check back shortly.")

# --------------------------------------------------
# PAGE 2: INTERNATIONAL PRICES
# --------------------------------------------------

elif page == "International Prices":

    st.markdown('<div class="page-eyebrow">Markets</div>', unsafe_allow_html=True)
    st.title("International Prices")
    st.markdown("Monthly historical series. Source: Yahoo Finance.")
    st.divider()

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))
    with col2:
        months = st.slider("Period (months)", min_value=6, max_value=60, value=24, step=6)

    with st.spinner(""):
        df = get_commodity_prices(commodity, months=months)

    if not df.empty:
        fig = px.line(
            df, x="date", y="price",
            title=f"{commodity} — {months} month history",
            labels={"date": "", "price": "Price"},
            line_shape="spline",
        )
        fig.update_traces(line_color="#C9A547", line_width=2.5,
                          fill="tozeroy", fillcolor="rgba(201,165,71,0.06)")
        fig.update_layout(
            title_font=dict(family="DM Serif Display", size=18, color="#E8EDF2"),
            **PLOT_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Current", f"{float(df['price'].iloc[-1]):.2f}")
        col_b.metric("High", f"{float(df['price'].max()):.2f}")
        col_c.metric("Low", f"{float(df['price'].min()):.2f}")
    else:
        st.warning("No data available for this commodity.")

# --------------------------------------------------
# PAGE 3: BRAZIL EXPORTS
# --------------------------------------------------

elif page == "Brazil Exports":

    st.markdown('<div class="page-eyebrow">Trade</div>', unsafe_allow_html=True)
    st.title("Brazil Exports")
    st.markdown("Export volume by commodity. Source: USDA PSD.")
    st.divider()

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))
    with col2:
        year = st.selectbox("Year", [2024, 2023, 2022, 2021], index=0)

    with st.spinner(""):
        df_exp = get_exports_by_commodity(commodity, year)

    if not df_exp.empty:
        st.markdown(f"### {commodity} exports — {year}")
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
    else:
        st.info("Export data unavailable for this selection.")

# --------------------------------------------------
# PAGE 4: BRL VS COMMODITIES
# --------------------------------------------------

elif page == "BRL vs Commodities":

    st.markdown('<div class="page-eyebrow">Analysis</div>', unsafe_allow_html=True)
    st.title("BRL vs Commodities")
    st.markdown("Correlation between exchange rate and international commodity prices.")
    st.divider()

    commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))

    with st.spinner(""):
        df_fx  = get_brl_usd(days=365)
        df_com = get_commodity_prices(commodity, months=12)

    if not df_fx.empty and not df_com.empty:
        df_fx  = df_fx.set_index("date").resample("ME").last().reset_index()
        df_com = df_com.set_index("date").resample("ME").last().reset_index()
        df_merged = pd.merge(df_fx, df_com, on="date", how="inner")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_merged["date"], y=df_merged["brl_usd"],
            name="BRL/USD",
            line=dict(color="#00C896", width=2.5),
            yaxis="y1",
        ))
        fig.add_trace(go.Scatter(
            x=df_merged["date"], y=df_merged["price"],
            name=commodity,
            line=dict(color="#C9A547", width=2.5),
            yaxis="y2",
        ))
        fig.update_layout(
            title=f"BRL/USD vs {commodity} — 12 months",
            title_font=dict(family="DM Serif Display", size=18, color="#E8EDF2"),
            yaxis=dict(title="BRL/USD", titlefont=dict(color="#00C896"), tickfont=dict(color="#00C896")),
            yaxis2=dict(title="Price", titlefont=dict(color="#C9A547"), tickfont=dict(color="#C9A547"),
                        overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(0,0,0,0)", bordercolor="#1E2A36"),
            **PLOT_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True)

        if len(df_merged) >= 3:
            corr = df_merged["brl_usd"].corr(df_merged["price"])
            direction = "positive" if corr > 0 else "negative"
            st.metric(
                label=f"Correlation — BRL/USD × {commodity}",
                value=f"{corr:.2f}",
                delta=f"{direction} correlation",
            )
    else:
        st.warning("Insufficient data for this analysis.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Commodity Monitor · Brazil · hugotolomei.com · Data: Yahoo Finance · USDA PSD · BCB")
