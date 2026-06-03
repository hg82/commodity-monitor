"""
fx.py
Fetches BRL/USD exchange rate from the Brazilian Central Bank public API.
No authentication required.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta


def get_brl_usd(days: int = 90) -> pd.DataFrame:
    end   = datetime.today()
    start = end - timedelta(days=days)

    url = (
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.10813/dados"
        f"?formato=json&dataInicial={start.strftime('%d/%m/%Y')}"
        f"&dataFinal={end.strftime('%d/%m/%Y')}"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
        df.columns = ["date", "brl_usd"]
        df["date"]    = pd.to_datetime(df["date"], dayfirst=True)
        df["brl_usd"] = pd.to_numeric(df["brl_usd"], errors="coerce")
        df = df.dropna().sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return pd.DataFrame(columns=["date", "brl_usd"])


def get_current_rate() -> float:
    df = get_brl_usd(days=7)
    if df.empty:
        return None
    return df["brl_usd"].iloc[-1]
