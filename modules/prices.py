"""
prices.py
Fetches international commodity prices from the World Bank Commodity Price API.
"""

import requests
import pandas as pd


COMMODITIES = {
    "Soybeans": "PSOYBSUSA",
    "Corn":     "PMAIZMTUSA",
    "Wheat":    "PWHEAMTUSD",
    "Coffee":   "PCOFFOTMUSD",
    "Sugar":    "PSUGAISAUSD",
    "Cocoa":    "PCOCOA",
}

COMMODITY_UNITS = {
    "Soybeans": "USD/mt",
    "Corn":     "USD/mt",
    "Wheat":    "USD/mt",
    "Coffee":   "USD/kg",
    "Sugar":    "USD/kg",
    "Cocoa":    "USD/mt",
}


def get_commodity_prices(commodity: str, months: int = 24) -> pd.DataFrame:
    code = COMMODITIES.get(commodity)
    if not code:
        return pd.DataFrame(columns=["date", "price"])

    url = (
        f"https://api.worldbank.org/v2/en/indicator/{code}"
        f"?format=json&mrv={months}&frequency=M"
    )

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        raw = resp.json()

        if len(raw) < 2 or not raw[1]:
            return pd.DataFrame(columns=["date", "price"])

        records = []
        for item in raw[1]:
            if item.get("value") is not None:
                records.append({
                    "date":  pd.to_datetime(item["date"], format="%YM%m"),
                    "price": float(item["value"])
                })
