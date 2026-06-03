"""
app.py
Commodity Price Monitor / Brazil
Author: Hugo Tolomei | hugotolomei.com
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from modules.prices import (
    get_commodity_prices,
    get_latest_prices,
    COMMODITIES,
)

from modules.exports import (
    get_exports_by_commodity,
    get_annual_exports_summary,
)

from modules.fx import (
    get_brl_usd,
    get_current_rate,
)

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
.block-container {
    padding-top: 2rem;
}

.stMetric {
    background: #0e1117;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 1rem;
}

h1, h2, h3 {
    font-family: Georgia, serif;
}
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
        [
            "Overview",
            "International Prices",
            "Brazil Exports",
            "BRL vs Commodities",
        ],
        index=0,
    )

    st.divider()

    st.markdown("**Data sources**")
    st.markdown("- Yahoo Finance")
    st.markdown("- Comex Stat / MDIC")
    st.markdown("- Banco Central do Brasil")

# --------------------------------------------------
# PAGE 1
# --------------------------------------------------

if page == "Overview":

    st.title("Commodity Price Monitor / Brazil")

    st.markdown(
        "International prices and Brazilian export data for grains and soft commodities."
    )

    st.divider()

    col1, col2 = st.columns([2, 1])

    # --------------------------
    # Prices
    # --------------------------

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

            st.warning(
                "Could not load commodity prices."
            )

    # --------------------------
    # FX
    # --------------------------

    with col2:

        st.subheader("USD/BRL Rate")

        rate = get_current_rate()

        if rate:

            st.metric(
                "Current rate",
                f"R$ {rate:.4f}"
            )

        else:

            st.warning(
                "Exchange rate unavailable."
            )

    st.divider()

    # --------------------------
    # EXPORTS
    # --------------------------

    st.subheader(
        "Export summary by commodity (latest available year)"
    )

    with st.spinner(
        "Loading export data..."
    ):

        df_exp = get_annual_exports_summary(
            year=2023
        )

    # DEBUG
    with st.expander(
        "Export Debug Information"
    ):
        st.write(
            "DataFrame type:",
            type(df_exp)
        )

        st.write(
            "Rows:",
            len(df_exp)
        )

        st.write(df_exp)

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

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.error(
            "Export DataFrame is empty."
        )

# --------------------------------------------------
# PAGE 2
# --------------------------------------------------

elif page == "International Prices":

    st.title("International Prices")

    commodity = st.selectbox(
        "Commodity",
        list(COMMODITIES.keys())
    )

    months = st.slider(
        "Months",
        min_value=6,
        max_value=60,
        value=24,
        step=6,
    )

    df = get_commodity_prices(
        commodity,
        months=months
    )

    if not df.empty:

        fig = px.line(
            df,
            x="date",
            y="price",
            title=f"{commodity} price history",
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(df.tail())

    else:

        st.warning(
            "No commodity data available."
        )

# --------------------------------------------------
# PAGE 3
# --------------------------------------------------

elif page == "Brazil Exports":

    st.title("Brazil Exports")

    commodity = st.selectbox(
        "Commodity",
        list(COMMODITIES.keys())
    )

    year = st.selectbox(
        "Year",
        [2023, 2022, 2021],
        index=0,
    )

    df_exp = get_exports_by_commodity(
        commodity,
        year
    )

    st.write(
        "Rows:",
        len(df_exp)
    )

    st.write(df_exp)

# --------------------------------------------------
# PAGE 4
# --------------------------------------------------

elif page == "BRL vs Commodities":

    st.title("BRL vs Commodities")

    commodity = st.selectbox(
        "Commodity",
        list(COMMODITIES.keys())
    )

    df_fx = get_brl_usd(
        days=365
    )

    df_com = get_commodity_prices(
        commodity,
        months=12
    )

    st.write(
        "FX rows:",
        len(df_fx)
    )

    st.write(
        "Commodity rows:",
        len(df_com)
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Commodity Price Monitor / Brazil"
)
