import requests
import pandas as pd
from datetime import datetime

API_URL = "https://api-comexstat.mdic.gov.br/general"

# NCM codes como inteiros (sem zero à esquerda, sem aspas)
# Soja: 1201001 | Milho: 10059010 | Café: 9011110 | Açúcar: 17011400 | Carne bovina: 2013000
COMMODITIES = {
    "Soja": [1201001, 1202900],
    "Milho": [10059010],
    "Café": [9011110, 9011200],
    "Açúcar": [17011400, 17019900],
    "Carne Bovina": [2013000, 2023000],
    "Celulose": [47032100, 47032900],
}

def get_exports(months: int = 12) -> pd.DataFrame:
    """
    Busca exportações brasileiras por commodity via Comex Stat.
    Retorna DataFrame com colunas: commodity, year, metricFOB, metricKG
    """
    today = datetime.today()
    # Período: últimos N meses
    end_year = today.year
    end_month = today.month - 1 if today.month > 1 else 12
    end_year = end_year if today.month > 1 else end_year - 1

    start_month = end_month - months + 1
    start_year = end_year
    if start_month <= 0:
        start_month += 12
        start_year -= 1

    period_from = f"{start_year}-{start_month:02d}"
    period_to   = f"{end_year}-{end_month:02d}"

    all_rows = []

    for commodity_name, ncm_codes in COMMODITIES.items():
        payload = {
            "flow": "export",
            "monthDetail": False,
            "period": {
                "from": period_from,
                "to": period_to
            },
            "filters": [
                {
                    "filter": "ncm",
                    "values": ncm_codes  # lista de inteiros
                }
            ],
            "details": ["ncm"],
            "metrics": ["metricFOB", "metricKG"]
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            rows = data.get("data", {}).get("list", [])

            if rows:
                df = pd.DataFrame(rows)
                df["commodity"] = commodity_name
                all_rows.append(df)

        except requests.exceptions.RequestException as e:
            print(f"[exports.py] Erro ao buscar {commodity_name}: {e}")
            continue

    if not all_rows:
        return pd.DataFrame(columns=["commodity", "year", "metricFOB", "metricKG"])

    result = pd.concat(all_rows, ignore_index=True)

    # Agrupa por commodity (soma todos os NCMs da mesma categoria)
    if "metricFOB" in result.columns and "metricKG" in result.columns:
        result = (
            result
            .groupby("commodity", as_index=False)
            .agg({"metricFOB": "sum", "metricKG": "sum"})
        )

    return result
