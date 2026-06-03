"""
scripts/fetch_exports.py
Fetches Brazilian export data from Comex Stat API and saves to data/exports_*.csv
Runs via GitHub Actions (scheduled) — not inside Streamlit Cloud.
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime

API_URL = "https://api-comexstat.mdic.gov.br/general"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# NCM codes as integers (no leading zeros, no quotes)
NCM_MAP = {
    "Soybeans": [1201001, 1202900],
    "Corn":     [10059010],
    "Wheat":    [10019900, 10011900],
    "Coffee":   [9011110, 9011200, 9012100],
    "Sugar":    [17011400, 17019900],
    "Cocoa":    [18010000, 18031000],
}

YEARS = [2021, 2022, 2023, 2024]

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def fetch_by_country(commodity: str, ncm_codes: list, year: int) -> pd.DataFrame:
    """Fetch top destinations for one commodity/year."""
    payload = {
        "flow": "export",
        "monthDetail": False,
        "period": {"from": f"{year}-01", "to": f"{year}-12"},
        "filters": [{"filter": "ncm", "values": ncm_codes}],
        "details": ["country"],
        "metrics": ["metricFOB", "metricKG"],
    }
    r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    rows = r.json().get("data", {}).get("list", [])
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["commodity"] = commodity
    df["year"] = year
    return df


def fetch_annual_summary(commodity: str, ncm_codes: list, year: int) -> dict:
    """Fetch total FOB for one commodity/year (no country breakdown)."""
    payload = {
        "flow": "export",
        "monthDetail": False,
        "period": {"from": f"{year}-01", "to": f"{year}-12"},
        "filters": [{"filter": "ncm", "values": ncm_codes}],
        "details": ["ncm"],
        "metrics": ["metricFOB"],
    }
    r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    rows = r.json().get("data", {}).get("list", [])
    total = sum(row.get("metricFOB", 0) for row in rows)
    return {"Commodity": commodity, "Exports (USD)": total, "year": year}


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- 1. By-country data (Page 3) ---
    print("Fetching by-country data...")
    all_country_rows = []

    for commodity, ncm_codes in NCM_MAP.items():
        for year in YEARS:
            print(f"  {commodity} {year}...", end=" ")
            try:
                df = fetch_by_country(commodity, ncm_codes, year)
                if not df.empty:
                    all_country_rows.append(df)
                    print(f"OK ({len(df)} rows)")
                else:
                    print("0 rows")
            except Exception as e:
                print(f"ERROR: {e}")

    if all_country_rows:
        df_country = pd.concat(all_country_rows, ignore_index=True)
        path = os.path.join(DATA_DIR, "exports_by_country.csv")
        df_country.to_csv(path, index=False)
        print(f"\nSaved: {path} ({len(df_country)} rows)")
    else:
        print("WARNING: no by-country data fetched")

    # --- 2. Annual summary (Page 1) ---
    print("\nFetching annual summary...")
    summary_rows = []

    for commodity, ncm_codes in NCM_MAP.items():
        for year in YEARS:
            print(f"  {commodity} {year}...", end=" ")
            try:
                row = fetch_annual_summary(commodity, ncm_codes, year)
                summary_rows.append(row)
                print(f"OK (USD {row['Exports (USD)']:,.0f})")
            except Exception as e:
                print(f"ERROR: {e}")

    if summary_rows:
        df_summary = pd.DataFrame(summary_rows)
        path = os.path.join(DATA_DIR, "exports_summary.csv")
        df_summary.to_csv(path, index=False)
        print(f"\nSaved: {path} ({len(df_summary)} rows)")
    else:
        print("WARNING: no summary data fetched")

    # --- 3. Metadata ---
    meta = {"last_updated": datetime.utcnow().isoformat() + "Z"}
    with open(os.path.join(DATA_DIR, "exports_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nDone. Last updated: {meta['last_updated']}")


if __name__ == "__main__":
    main()
