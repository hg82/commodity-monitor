"""
prices.py
Fetches international commodity prices from the World Bank Commodity Price API.
Documentation: https://api.worldbank.org/v2/en/indicator
"""

import requests
import pandas as pd


# Commodity name -> World Bank code
COMMODITIES = {
    "Soybeans": "SOYBEANS",
    "Corn":     "MAIZE",
    "Wheat":    "WHEAT",
    "Coffee":   "COFFEE_ARABIC",
    "Sugar":    "SUGAR_WLD",
    "Cocoa":    "COCOA",
}

COMMODITY_UNITS = {
    "Soybeans": "USD/mt",
    "Corn":     "USD/mt",
    "Wheat":    "USD/mt",
    "Coffee":   "USc/kg",
    "Sugar":    "USc/kg",
    "Cocoa":    "USD/mt",
}


def get_commodity_prices(commodity: str, months: int = 24) -> pd.DataFrame:
    code = COMMODITIES.get(commodity)
    if not code:
        return pd.DataFrame(columns=["date", "price"])

    url = (
        f"https://api.worldbank.org/v2/en/indicator/PCOMM.{code}"
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

        df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
        return df

    except Exception as e:
        print(f"Error fetching prices for {commodity}: {e}")
        return pd.DataFrame(columns=["date", "price"])


def get_latest_prices() -> pd.DataFrame:
    rows = []
    for name in COMMODITIES:
        df = get_commodity_prices(name, months=3)
        if not df.empty:
            latest = df.iloc[-1]
            prev   = df.iloc[-2] if len(df) >= 2 else latest
            change = ((latest["price"] - prev["price"]) / prev["price"]) * 100
            rows.append({
                "Commodity": name,
                "Price":     latest["price"],
                "Unit":      COMMODITY_UNITS[name],
                "Change %":  round(change, 2),
                "Date":      latest["date"].strftime("%b/%Y"),
            })
    return pd.DataFrame(rows)
