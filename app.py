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

st.set_page_config(
    page_title="Commodity Monitor | Brazil",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg:         #FFFFFF;
    --bg2:        #F7F8FA;
    --bg3:        #F0F2F5;
    --border:     #E2E6EA;
    --navy:       #1A2A4A;
    --navy-light: #2E4070;
    --gold:       #B8963E;
    --green:      #1A7A4A;
    --red:        #C0392B;
    --text:       #1A1A2E;
    --text-mid:   #4A5568;
    --text-muted: #8A96A3;
    --font:       'Inter', system-ui, sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--font) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    padding: 2.5rem 3rem 4rem;
    max-width: 1200px;
    background: var(--bg);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
[data-testid="stSidebar"] * { color: #CBD5E0 !important; }
[data-testid="stSidebar"] .block-container { padding: 2rem 1.4rem; }

/* RADIO NAV */
[data-testid="stRadio"] label {
    font-size: 1rem !important;
    font-weight: 400 !important;
    color: #A0AEC0 !important;
    padding: 0.5rem 0 !important;
}
[data-testid="stRadio"] label:hover { color: #FFFFFF !important; }

/* HEADINGS */
h1 {
    font-size: 3rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: var(--navy) !important;
    line-height: 1.1 !important;
    margin-bottom: 0.4rem !important;
}
h2 {
    font-size: 1.7rem !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
}
h3 {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    margin-bottom: 1rem !important;
}

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2rem 0 !important;
}

/* METRICS */
[data-testid="stMetric"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1.4rem 1.6rem !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
}

/* SELECTBOX */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
}

/* ALERT */
[data-testid="stAlert"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
    color: var(--text-mid) !important;
}

/* CAPTION */
[data-testid="stCaptionContainer"] {
    font-size: 0.75rem !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.02em !important;
}

/* PRICE ROW */
.price-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.6rem;
    background: var(--bg);
    border: 1px solid var(--border);
    border-left: 4px solid var(--navy);
    border-radius: 8px;
    margin-bottom: 0.6rem;
    transition: box-shadow 0.2s, transform 0.15s;
}
.price-row:hover {
    box-shadow: 0 2px 16px rgba(26,42,74,0.09);
    transform: translateX(3px);
}
.price-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--navy);
    min-width: 120px;
}
.price-value {
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--text);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
}
.price-unit {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-left: 5px;
    font-weight: 400;
}
.price-change-up {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--green);
    background: #E8F5EE;
    padding: 4px 12px;
    border-radius: 20px;
    font-variant-numeric: tabular-nums;
    min-width: 80px;
    text-align: center;
}
.price-change-down {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--red);
    background: #FDF0EE;
    padding: 4px 12px;
    border-radius: 20px;
    font-variant-numeric: tabular-nums;
    min-width: 80px;
    text-align: center;
}
.price-date {
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 400;
    min-width: 70px;
    text-align: right;
}

/* EYEBROW */
.page-eyebrow {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.5rem;
}

/* RATE CARD */
.rate-card {
    background: var(--navy);
    border-radius: 12px;
    padding: 2.2rem 1.8rem;
    text-align: center;
}
.rate-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin-bottom: 0.7rem;
}
.rate-value {
    font-size: 3rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}
.rate-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
    margin-top: 0.6rem;
    letter-spacing: 0.04em;
}

/* SIDEBAR BRAND */
.sidebar-brand-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.01em;
}
.sidebar-brand-sub {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gold);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 4px;
}
.sidebar-section-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.28);
    margin: 2rem 0 0.8rem;
}
.sidebar-source {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.5);
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
</style>
""", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Inter, system-ui, sans-serif", color="#1A1A2E", size=13),
    xaxis=dict(gridcolor="#E2E6EA", linecolor="#E2E6EA",
               tickfont=dict(size=12, color="#8A96A3")),
    yaxis=dict(gridcolor="#E2E6EA", linecolor="#E2E6EA",
               tickfont=dict(size=12, color="#8A96A3")),
    margin=dict(l=10, r=10, t=55, b=10),
    hoverlabel=dict(bgcolor="#1A2A4A", font_size=13,
                    font_color="#FFFFFF", bordercolor="#1A2A4A"),
)

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.5rem">
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
    <div class="sidebar-source">USDA PSD</div>
    <div class="sidebar-source">Banco Central do Brasil</div>
    """, unsafe_allow_html=True)

# PAGE 1: OVERVIEW
if page == "Overview":

    st.markdown('<div class="page-eyebrow">Dashboard</div>', unsafe_allow_html=True)
    st.title("Commodity Monitor")
    st.markdown(
        "<p style='font-size:1.05rem;color:#4A5568;margin-top:0.2rem'>"
        "International prices and Brazilian export data for grains and soft commodities."
        "</p>", unsafe_allow_html=True
    )
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
            x="Commodity", y="Exports (USD)",
            color="Commodity",
            color_discrete_sequence=["#1A2A4A","#2E4070","#B8963E","#1A7A4A","#5A8FC0","#8A96A3"],
            title="Brazilian exports by commodity (2023)",
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            showlegend=False,
            title_font=dict(family="Inter", size=16, color="#1A2A4A"),
            **PLOT_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Export data is being fetched. Check back shortly.")

# PAGE 2: INTERNATIONAL PRICES
elif page == "International Prices":

    st.markdown('<div class="page-eyebrow">Markets</div>', unsafe_allow_html=True)
    st.title("International Prices")
    st.markdown(
        "<p style='font-size:1.05rem;color:#4A5568'>Monthly historical series. Source: Yahoo Finance.</p>",
        unsafe_allow_html=True
    )
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
        fig.update_traces(
            line_color="#1A2A4A", line_width=2.5,
            fill="tozeroy", fillcolor="rgba(26,42,74,0.05)",
        )
        fig.update_layout(
            title_font=dict(family="Inter", size=16, color="#1A2A4A"),
            **PLOT_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Current", f"{float(df['price'].iloc[-1]):.2f}")
        col_b.metric("High", f"{float(df['price'].max()):.2f}")
        col_c.metric("Low", f"{float(df['price'].min()):.2f}")
    else:
        st.warning("No data available for this commodity.")

# PAGE 3: BRAZIL EXPORTS
elif page == "Brazil Exports":

    st.markdown('<div class="page-eyebrow">Trade</div>', unsafe_allow_html=True)
    st.title("Brazil Exports")
    st.markdown(
        "<p style='font-size:1.05rem;color:#4A5568'>Export volume by commodity. Source: USDA PSD.</p>",
        unsafe_allow_html=True
    )
    st.divider()

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))
    with col2:
        year = st.selectbox("Year", [2024, 2023, 2022, 2021], index=0)

    with st.spinner(""):
        df_exp = get_exports_by_commodity(commodity, year)

    if not df_exp.empty:
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
    else:
        st.info("Export data unavailable for this selection.")

# PAGE 4: BRL VS COMMODITIES
elif page == "BRL vs Commodities":

    st.markdown('<div class="page-eyebrow">Analysis</div>', unsafe_allow_html=True)
    st.title("BRL vs Commodities")
    st.markdown(
        "<p style='font-size:1.05rem;color:#4A5568'>Correlation between exchange rate and international commodity prices.</p>",
        unsafe_allow_html=True
    )
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
            name="BRL/USD", line=dict(color="#1A7A4A", width=2.5), yaxis="y1",
        ))
        fig.add_trace(go.Scatter(
            x=df_merged["date"], y=df_merged["price"],
            name=commodity, line=dict(color="#1A2A4A", width=2.5), yaxis="y2",
        ))
        fig.update_layout(
            title=f"BRL/USD vs {commodity} — 12 months",
            title_font=dict(family="Inter", size=16, color="#1A2A4A"),
            yaxis=dict(title="BRL/USD", titlefont=dict(color="#1A7A4A", size=13),
                       tickfont=dict(color="#1A7A4A")),
            yaxis2=dict(title="Price", titlefont=dict(color="#1A2A4A", size=13),
                        tickfont=dict(color="#1A2A4A"),
                        overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(0,0,0,0)", bordercolor="#E2E6EA",
                        font=dict(size=13)),
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

# FOOTER
st.divider()
st.caption("Commodity Monitor · Brazil · hugotolomei.com · Data: Yahoo Finance · USDA PSD · BCB")
