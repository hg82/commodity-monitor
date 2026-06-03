"""
exports.py
Fetches Brazilian export data from the Comex Stat API (MDIC - Ministry of Trade).
Documentation: https://api-comexstat.mdic.gov.br
"""

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


def get_exports_by_commodity(commodity: str, year: int = 2023) -> pd.DataFrame:
    ncm_list = NCM_GROUPS.get(commodity, [])
    if not ncm_list:
        return pd.DataFrame()

    params = {
        "flow":       "export",
        "yearStart":  year,
        "yearEnd":    year,
        "monthStart": 1,
        "monthEnd":   12,
        "ncm":        ",".join(ncm_list),
        "groupBy":    "country",
        "details":    "false",
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("data"):
            return pd.DataFrame()

        df = pd.DataFrame(data["data"])
        df = df.rename(columns={
            "noCountry": "Destination",
            "metricFOB": "FOB Value (USD)",
            "metricKG":  "Weight (kg)",
        })

        cols = ["Destination", "FOB Value (USD)", "Weight (kg)"]
        df = df[[c for c in cols if c in df.columns]]
        df["FOB Value (USD)"] = pd.to_numeric(df["FOB Value (USD)"], errors="coerce")
        df = df.dropna(subset=["FOB Value (USD)"])
        df = df.sort_values("FOB Value (USD)", ascending=False).reset_index(drop=True)
        df["FOB Value (USD)"] = df["FOB Value (USD)"].apply(lambda x: f"${x:,.0f}")
        return df.head(15)

    except Exception as e:
        print(f"Error fetching exports for {commodity}: {e}")
        return pd.DataFrame()


def get_annual_exports_summary(year: int = 2023) -> pd.DataFrame:
    rows = []
    for commodity in NCM_GROUPS:
        ncm_list = NCM_GROUPS[commodity]
        params = {
            "flow":       "export",
            "yearStart":  year,
            "yearEnd":    year,
            "monthStart": 1,
            "monthEnd":   12,
            "ncm":        ",".join(ncm_list),
            "details":    "false",
        }
        try:
            resp = requests.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if data.get("data"):
                total = sum(
                    float(r.get("metricFOB", 0))
                    for r in data["data"]
                    if r.get("metricFOB")
                )
                rows.append({"Commodity": commodity, "Exports (USD)": total, "Year": year})
        except Exception as e:
            print(f"Error in summary for {commodity}: {e}")

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Exports (USD)", ascending=False).reset_index(drop=True)
    return df
