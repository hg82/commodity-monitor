import yfinance as yf
import pandas as pd

COMMODITIES = {
    "Soybeans": "ZS=F",
    "Corn":     "ZC=F",
    "Wheat":    "ZW=F",
    "Coffee":   "KC=F",
    "Sugar":    "SB=F",
    "Cocoa":    "CC=F",
}

COMMODITY_UNITS = {
    "Soybeans": "USc/bu",
    "Corn":     "USc/bu",
    "Wheat":    "USc/bu",
    "Coffee":   "USc/lb",
    "Sugar":    "USc/lb",
    "Cocoa":    "USD/mt",
}


def get_commodity_prices(commodity, months=24):
    ticker = COMMODITIES.get(commodity)
    if not ticker:
        return pd.DataFrame(columns=["date", "price"])
    try:
        period = str(months) + "mo"
        df = yf.download(ticker, period=period, interval="1mo", progress=False)
        if df.empty:
            return pd.DataFrame(columns=["date", "price"])
        df = df[["Close"]].reset_index()
        df.columns = ["date", "price"]
        df["price"] = df["price"].astype(float).round(2)
        df = df.dropna().sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print("Error: " + str(e))
        return pd.DataFrame(columns=["date", "price"])


def get_latest_prices():
    rows = []
    for name in COMMODITIES:
        df = get_commodity_prices(name, months=2)
        if not df.empty:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else latest
            change = ((latest["price"] - prev["price"]) / prev["price"]) * 100
            rows.append({
                "Commodity": name,
                "Price": round(float(latest["price"]), 2),
                "Unit": COMMODITY_UNITS[name],
                "Change %": round(change, 2),
                "Date": latest["date"].strftime("%b/%Y"),
            })
    return pd.DataFrame(rows)
