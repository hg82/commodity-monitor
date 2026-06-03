import requests
import pandas as pd

COMMODITIES = {
    "Soybeans": "PSOYBSUSA",
    "Corn": "PMAIZMTUSA",
    "Wheat": "PWHEAMTUSD",
    "Coffee": "PCOFFOTMUSD",
    "Sugar": "PSUGAISAUSD",
    "Cocoa": "PCOCOA",
}

COMMODITY_UNITS = {
    "Soybeans": "USD/mt",
    "Corn": "USD/mt",
    "Wheat": "USD/mt",
    "Coffee": "USD/kg",
    "Sugar": "USD/kg",
    "Cocoa": "USD/mt",
}


def get_commodity_prices(commodity, months=24):
    code = COMMODITIES.get(commodity)
    if not code:
        return pd.DataFrame(columns=["date", "price"])
    url = (
        "https://api.worldbank.org/v2/en/indicator/" + code
        + "?format=json&mrv=" + str(months) + "&frequency=M"
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
                    "date": pd.to_datetime(item["date"], format="%YM%m"),
                    "price": float(item["value"])
                })
        df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print("Error: " + str(e))
        return pd.DataFrame(columns=["date", "price"])


def get_latest_prices():
    rows = []
    for name in COMMODITIES:
        df = get_commodity_prices(name, months=3)
        if not df.empty:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else latest
            change = ((latest["price"] - prev["price"]) / prev["price"]) * 100
            rows.append({
                "Commodity": name,
                "Price": latest["price"],
                "Unit": COMMODITY_UNITS[name],
                "Change %": round(change, 2),
                "Date": latest["date"].strftime("%b/%Y"),
            })
    return pd.DataFrame(rows)
