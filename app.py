"""
app.py
Commodity Price Monitor / Brazil
Author: Hugo Tolomei | hugotolomei.com
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
.block-container { padding-top: 2rem; }
.stMetric { background: #0e1117; border: 1px solid #2a2a2a; border-radius: 6px; padding: 1rem; }
h1, h2, h3 { font-family: Georgia, serif; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🌾 Commodity Monitor")
    st.markdown("**Brazil** | hugotolomei.com")
    st.divider()
    page = st.radio(
        "Navigation",
        ["Overview", "International Prices", "Brazil Exports", "BRL vs Commodities"],
        index=0,
    )
    st.divider()
    st.markdown("**Data sources**")
    st.markdown("- Yahoo Finance")
    st.markdown("- Comex Stat / MDIC")
    st.markdown("- Banco Central do Brasil")

# --------------------------------------------------
# PAGE 1: OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.title("Commodity Price Monitor / Brazil")
    st.markdown("International prices and Brazilian export data for grains and soft commodities.")
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Latest prices")
        with st.spinner("Loading prices..."):
            df_prices = get_latest_prices()
        if not df_prices.empty:
            for _, row in df_prices.iterrows():
                icon = "🟢" if row["Change %"] >= 0 else "🔴"
                st.markdown(
                    f"**{row['Commodity']}** "
                    f"&nbsp; {row['Price']:.2f} {row['Unit']} "
                    f"&nbsp; {icon} {row['Change %']:+.2f}% "
                    f"&nbsp; *({row['Date']})*"
                )
        else:
            st.warning("Could not load commodity prices.")

    with col2:
        st.subheader("USD/BRL Rate")
        rate = get_current_rate()
        if rate:
            st.metric("Current rate", f"R$ {rate:.4f}")
        else:
            st.warning("Exchange rate unavailable.")

    st.divider()

    st.subheader("Export summary by commodity (latest available year)")

    with st.spinner("Loading export data..."):
        df_exp = get_annual_exports_summary(year=2023)

    with st.expander("Export Debug Information"):
        st.write("DataFrame type: " + str(type(df_exp)))
        st.write("Rows: " + str(len(df_exp)))
        st.dataframe(df_exp)

    if not df_exp.empty:
        fig = px.bar(
            df_exp,
            x="Commodity",
            y="Exports (USD)",
            color="Commodity",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Brazilian exports by commodity (2023)",
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font_color="#fafafa",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Export data currently unavailable.")

# --------------------------------------------------
# PAGE 2: INTERNATIONAL PRICES
# --------------------------------------------------

elif page == "International Prices":

    st.title("International Prices")
    st.markdown("Monthly historical series. Source: Yahoo Finance.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))
    with col2:
        months = st.slider("Period (months)", min_value=6, max_value=60, value=24, step=6)

    with st.spinner("Loading " + commodity + " data..."):
        df = get_commodity_prices(commodity, months=months)

    if not df.empty:
        fig = px.line(
            df, x="date", y="price",
            title=commodity + " price history (" + str(months) + " months)",
            labels={"date": "Date", "price": "Price"},
            line_shape="spline",
        )
        fig.update_traces(line_color="#C9A547", line_width=2)
        fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="#fafafa")
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Current price", str(round(float(df["price"].iloc[-1]), 2)))
        col_b.metric("High", str(round(float(df["price"].max()), 2)))
        col_c.metric("Low", str(round(float(df["price"].min()), 2)))
    else:
        st.warning("No data available for this commodity.")

# --------------------------------------------------
# PAGE 3: BRAZIL EXPORTS
# --------------------------------------------------

elif page == "Brazil Exports":

    st.title("Brazil Exports")
    st.markdown("Top destinations by commodity. Source: Comex Stat / MDIC.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))
    with col2:
        year = st.selectbox("Year", [2023, 2022, 2021], index=0)

    with st.spinner("Loading " + commodity + " export data..."):
        df_exp = get_exports_by_commodity(commodity, year)

    st.write("Rows: " + str(len(df_exp)))

    if not df_exp.empty:
        st.subheader("Top destinations — " + commodity + " (" + str(year) + ")")
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
    else:
        st.info("No export data available for this selection.")

# --------------------------------------------------
# PAGE 4: BRL VS COMMODITIES
# --------------------------------------------------

elif page == "BRL vs Commodities":

    st.title("BRL vs Commodities")
    st.markdown("Correlation between exchange rate and international commodity prices.")
    st.divider()

    commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))

    with st.spinner("Loading data..."):
        df_fx  = get_brl_usd(days=365)
        df_com = get_commodity_prices(commodity, months=12)

    st.write("FX rows: " + str(len(df_fx)))
    st.write("Commodity rows: " + str(len(df_com)))

    if not df_fx.empty and not df_com.empty:
        df_fx  = df_fx.set_index("date").resample("ME").last().reset_index()
        df_com = df_com.set_index("date").resample("ME").last().reset_index()
        df_merged = pd.merge(df_fx, df_com, on="date", how="inner")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_merged["date"], y=df_merged["brl_usd"],
            name="BRL/USD", line=dict(color="#4FC3F7", width=2), yaxis="y1"
        ))
        fig.add_trace(go.Scatter(
            x=df_merged["date"], y=df_merged["price"],
            name=commodity, line=dict(color="#C9A547", width=2), yaxis="y2"
        ))
        fig.update_layout(
            title="BRL/USD vs " + commodity + " (12 months)",
            yaxis=dict(title="BRL/USD", titlefont=dict(color="#4FC3F7")),
            yaxis2=dict(title="Price", titlefont=dict(color="#C9A547"), overlaying="y", side="right"),
            plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="#fafafa",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        if len(df_merged) >= 3:
            corr = df_merged["brl_usd"].corr(df_merged["price"])
            st.metric("Correlation BRL/USD x Price", str(round(corr, 2)))
    else:
        st.warning("Insufficient data for this chart.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Commodity Price Monitor / Brazil · hugotolomei.com · Data: Yahoo Finance, MDIC, BCB")
