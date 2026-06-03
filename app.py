"""
app.py
Commodity Price Monitor / Brazil
Autor: Hugo Tolomei | hugotolomei.com
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from modules.prices  import get_commodity_prices, get_latest_prices, COMMODITIES
from modules.exports import get_exports_by_commodity, get_annual_exports_summary
from modules.fx      import get_brl_usd, get_current_rate

# ── CONFIG ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Commodity Monitor | Brazil",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ESTILO ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .metric-label  { font-size: 0.75rem; color: #888; }
    .stMetric      { background: #0e1117; border: 1px solid #2a2a2a; border-radius: 6px; padding: 1rem; }
    h1, h2, h3    { font-family: Georgia, serif; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 Commodity Monitor")
    st.markdown("**Brazil** | hugotolomei.com")
    st.divider()

    pagina = st.radio(
        "Navegação",
        ["Visão Geral", "Preços Internacionais", "Exportações Brasil", "BRL vs Commodities"],
        index=0,
    )

    st.divider()
    st.markdown("**Fontes de dados**")
    st.markdown("- World Bank Pink Sheet")
    st.markdown("- Comex Stat / MDIC")
    st.markdown("- Banco Central do Brasil")
    st.caption("Dados públicos e gratuitos.")

# ── PÁGINA 1: VISÃO GERAL ────────────────────────────────────────────
if pagina == "Visão Geral":
    st.title("Commodity Price Monitor")
    st.markdown("Preços internacionais e exportações brasileiras de grãos e soft commodities.")
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Preços recentes")
        with st.spinner("Buscando preços..."):
            df_prices = get_latest_prices()

        if not df_prices.empty:
            for _, row in df_prices.iterrows():
                cor = "🟢" if row["Variação %"] >= 0 else "🔴"
                st.markdown(
                    f"**{row['Commodity']}** &nbsp; {row['Preço']:.2f} {row['Unidade']} "
                    f"&nbsp; {cor} {row['Variação %']:+.2f}% &nbsp; *('{row['Data']})*"
                )
        else:
            st.warning("Não foi possível carregar os preços. Verifique sua conexão.")

    with col2:
        st.subheader("Câmbio BRL/USD")
        taxa = get_current_rate()
        if taxa:
            st.metric("Cotação atual", f"R$ {taxa:.4f}", delta=None)
        else:
            st.warning("Câmbio indisponível.")

    st.divider()
    st.subheader("Exportações por commodity (último ano disponível)")
    with st.spinner("Buscando exportações..."):
        df_exp = get_annual_exports_summary(year=2023)

    if not df_exp.empty:
        fig = px.bar(
            df_exp,
            x="Commodity",
            y="Exportações (USD)",
            color="Commodity",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"Exportações (USD)": "USD"},
            title="Exportações brasileiras por commodity (2023)",
        )
        fig.update_layout(showlegend=False, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          font_color="#fafafa")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados de exportação indisponíveis no momento.")


# ── PÁGINA 2: PREÇOS INTERNACIONAIS ─────────────────────────────────
elif pagina == "Preços Internacionais":
    st.title("Preços Internacionais")
    st.markdown("Série histórica mensal. Fonte: World Bank Commodity Price Data (Pink Sheet).")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))
    with col2:
        meses = st.slider("Período (meses)", min_value=6, max_value=60, value=24, step=6)

    with st.spinner(f"Carregando dados de {commodity}..."):
        df = get_commodity_prices(commodity, months=meses)

    if not df.empty:
        fig = px.line(
            df, x="data", y="preco",
            title=f"{commodity} — Preço internacional ({meses} meses)",
            labels={"data": "Data", "preco": "Preço"},
            line_shape="spline",
        )
        fig.update_traces(line_color="#C9A547", line_width=2)
        fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="#fafafa")
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Preço atual",  f"{df['preco'].iloc[-1]:.2f}")
        col_b.metric("Máximo",       f"{df['preco'].max():.2f}")
        col_c.metric("Mínimo",       f"{df['preco'].min():.2f}")
    else:
        st.warning("Dados não disponíveis para esta commodity.")


# ── PÁGINA 3: EXPORTAÇÕES BRASIL ────────────────────────────────────
elif pagina == "Exportações Brasil":
    st.title("Exportações Brasileiras")
    st.markdown("Principais destinos por commodity. Fonte: Comex Stat / MDIC.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))
    with col2:
        ano = st.selectbox("Ano", [2023, 2022, 2021], index=0)

    with st.spinner(f"Buscando exportações de {commodity} ({ano})..."):
        df_exp = get_exports_by_commodity(commodity, year=ano)

    if not df_exp.empty:
        st.subheader(f"Top destinos — {commodity} ({ano})")
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
    else:
        st.info("Dados não disponíveis para esta seleção.")


# ── PÁGINA 4: BRL VS COMMODITIES ────────────────────────────────────
elif pagina == "BRL vs Commodities":
    st.title("BRL vs Commodities")
    st.markdown("Correlação entre câmbio e preços internacionais.")
    st.divider()

    commodity = st.selectbox("Commodity", list(COMMODITIES.keys()))

    with st.spinner("Carregando dados..."):
        df_fx  = get_brl_usd(days=365)
        df_com = get_commodity_prices(commodity, months=12)

    if not df_fx.empty and not df_com.empty:
        df_fx  = df_fx.set_index("data").resample("ME").last().reset_index()
        df_com = df_com.set_index("data").resample("ME").last().reset_index()
        df_merged = pd.merge(df_fx, df_com, on="data", how="inner")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_merged["data"], y=df_merged["brl_usd"],
            name="BRL/USD", line=dict(color="#4FC3F7", width=2), yaxis="y1"
        ))
        fig.add_trace(go.Scatter(
            x=df_merged["data"], y=df_merged["preco"],
            name=commodity, line=dict(color="#C9A547", width=2), yaxis="y2"
        ))
        fig.update_layout(
            title=f"BRL/USD vs {commodity} (12 meses)",
            yaxis=dict(title="BRL/USD", titlefont=dict(color="#4FC3F7")),
            yaxis2=dict(title="Preço", titlefont=dict(color="#C9A547"),
                        overlaying="y", side="right"),
            plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="#fafafa",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        if len(df_merged) >= 3:
            corr = df_merged["brl_usd"].corr(df_merged["preco"])
            st.metric("Correlação BRL/USD x Preço", f"{corr:.2f}",
                      help="1 = correlação perfeita positiva, -1 = inversa")
    else:
        st.warning("Dados insuficientes para o gráfico.")

# ── RODAPÉ ──────────────────────────────────────────────────────────
st.divider()
st.caption("Commodity Price Monitor / Brazil · hugotolomei.com · Dados: World Bank, MDIC, BCB")
