import requests
import pandas as pd

COMMODITIES = {
    "Soybeans": "PSOYB",
    "Corn":     "PMAIZ",
    "Wheat":    "PWHEAMT",
    "Coffee":   "PCOFFOTM",
    "Sugar":    "PSUGAR",
    "Cocoa":    "PCOCO",
}

COMMODITY_UNITS = {
    "Soybeans": "USD/mt",
    "Corn":     "USD/mt",
    "Wheat":    "USD/mt",
    "Coffee":   "USD/kg",
    "Sugar":    "USD/kg",
    "Cocoa":    "USD/mt",
}

IMF_URL = "https://www.imf.org/external/np/res/commod/data/PALLFNFINDEXM.csv"


def get_all_prices_imf():
    try:
        df = pd.read_csv(
            "https://www.imf.org/external/np/res/commod/data/PALLFNFINDEXM.csv",
            skiprows=1
        )
        return df
    except Exception as e:
        print("IMF fetch error: " + str(e))
        return pd.DataFrame()


def get_commodity_prices(commodity, months=24):
    IMF_CODES = {
        "Soybeans": "Soybeans",
        "Corn":     "Corn",
        "Wheat":    "Wheat, US HRW",
        "Coffee":   "Coffee, Robusta",
        "Sugar":    "Sugar, Free Market",
        "Cocoa":    "Cocoa beans",
    }
    col = IMF_CODES.get(commodity)
    if not col:
        return pd.DataFrame(columns=["date", "price"])
    try:
        df = pd.read_csv(
            "https://www.imf.org/external/np/res/commod/data/PALLFNFINDEXM.csv",
            skiprows=1
        )
        if "Date" not in df.columns:
            df.columns.values[0] = "Date"
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        matching = [c for c in df.columns if col.lower() in c.lower()]
        if not matching:
            return pd.DataFrame(columns=["date", "price"])
        df = df[["Date", matching[0]]].copy()
        df.columns = ["date", "price"]
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna().sort_values("date").tail(months).reset_index(drop=True)
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
                "Price": round(latest["price"], 2),
                "Unit": COMMODITY_UNITS[name],
                "Change %": round(change, 2),
                "Date": latest["date"].strftime("%b/%Y"),
            })
    return pd.DataFrame(rows)
