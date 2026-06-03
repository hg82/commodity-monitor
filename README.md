# 🌾 Commodity Price Monitor / Brazil

Dashboard interativo que cruza **preços internacionais** de commodities com **dados de exportação brasileira**.

Desenvolvido por [Hugo Tolomei](https://hugotolomei.com) — Senior Economic Policy Adviser.

---

## O que o projeto faz

| Tela | Conteúdo |
|---|---|
| Visão Geral | Preços recentes + câmbio + exportações resumidas |
| Preços Internacionais | Série histórica mensal por commodity |
| Exportações Brasil | Top destinos por commodity e ano |
| BRL vs Commodities | Correlação câmbio x preço internacional |

## Commodities monitoradas

Grãos: Soja, Milho, Trigo
Soft: Café, Açúcar, Cacau

## Fontes de dados

- **World Bank** — Commodity Price Data (Pink Sheet)
- **Comex Stat / MDIC** — Exportações brasileiras
- **Banco Central do Brasil** — Câmbio BRL/USD

Todas as fontes são públicas e gratuitas.

## Como rodar localmente

```bash
# Clonar o repositório
git clone https://github.com/hg82/commodity-monitor.git
cd commodity-monitor

# Instalar dependências
pip install -r requirements.txt

# Rodar o dashboard
streamlit run app.py
```

## Stack

Python · Streamlit · Plotly · Pandas · Requests

---

> Where Policy Meets Markets. — hugotolomei.com
