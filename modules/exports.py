import requests
import pandas as pd

NCM_GROUPS = {
    "Soybeans": ["1201", "1208", "2304"],
    "Corn":     ["1005"],
    "Wheat":    ["1001", "1101"],
    "Coffee":   ["0901", "2101"],
    "Sugar":    ["1701", "1702"],
    "Cocoa":    ["1801", "1802", "1803"],
}

BASE_URL = "https://api-comexstat.mdic.gov.br/general"


def get_exports_by_commodity(commodity, year=2023):
    ncm_list = NCM_GROUPS.get(commodity, [])
    if not ncm_list:
        return pd.DataFrame()
    try:
        payload = {
            "flow": "export",
            "monthDetail": False,
            "period": {"from": str(year) + "-01", "to": str(year) + "-12"},
            "filters": [{"filter": "ncm", "values": ncm_list}],
            "details": ["country"],
            "metrics": ["metricFOB"],
        }
        resp = requests.post(BASE_URL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("data", {}).get("list"):
            return pd.DataFrame()
        df = pd.DataFrame(data["data"]["list"])
        df = df.rename(columns={
            "noCountry": "Destination",
            "metricFOB": "FOB Value (USD)",
        })
        cols = ["Destination", "FOB Value (USD)"]
        df = df[[c for c in cols if c in df.columns]]
        df["FOB Value (USD)"] = pd.to_numeric(df["FOB Value (USD)"], errors="coerce")
        df = df.dropna().sort_values("FOB Value (USD)", ascending=False).head(15).reset_index(drop=True)
        df["FOB Value (USD)"] = df["FOB Value (USD)"].apply(lambda x: f"${x:,.0f}")
        return df
    except Exception as e:
        print("Error: " + str(e))
        return pd.DataFrame()


def get_annual_exports_summary(year=2023):
    rows = []
    for commodity, ncm_list in NCM_GROUPS.items():
        try:
            payload = {
                "flow": "export",
                "monthDetail": False,
                "period": {"from": str(year) + "-01", "to": str(year) + "-12"},
                "filters": [{"filter": "ncm", "values": ncm_list}],
                "details": [],
                "metrics": ["metricFOB"],
            }
            resp = requests.post(BASE_URL, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if data.get("data", {}).get("list"):
                total = sum(
                    float(r.get("metricFOB", 0))
                    for r in data["data"]["list"]
                    if r.get("metricFOB")
                )
                rows.append({"Commodity": commodity, "Exports (USD)": total, "Year": year})
        except Exception as e:
            print("Error " + commodity + ": " + str(e))
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Exports (USD)", ascending=False).reset_index(drop=True)
    return df
