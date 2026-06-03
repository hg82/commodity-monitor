# 🌾 Commodity Price Monitor / Brazil

Interactive dashboard tracking **international commodity prices** and **Brazilian export data** for grains and soft commodities.

Built by [Hugo Tolomei](https://hugotolomei.com) — Senior Economic Policy Adviser, London.

---

## What it does

| Screen | Content |
|---|---|
| Overview | Latest prices + exchange rate + export summary |
| International Prices | Monthly historical series by commodity |
| Brazil Exports | Top destinations by commodity and year |
| BRL vs Commodities | Correlation between exchange rate and prices |

## Commodities covered

**Grains:** Soybeans, Corn, Wheat
**Soft:** Coffee, Sugar, Cocoa

## Data sources

- **World Bank** — Commodity Price Data (Pink Sheet)
- **Comex Stat / MDIC** — Brazilian export statistics
- **Banco Central do Brasil** — BRL/USD exchange rate

All sources are public and free.

## Run locally

```bash
git clone https://github.com/hg82/commodity-monitor.git
cd commodity-monitor
pip install -r requirements.txt
streamlit run app.py
```

## Stack

Python · Streamlit · Plotly · Pandas · Requests

---

> Where Policy Meets Markets. — [hugotolomei.com](https://hugotolomei.com)
