"""
scripts/fetch_exports.py
Fetches Brazilian export data from USDA PSD API and saves to data/exports_*.csv
Runs via GitHub Actions (scheduled) — not inside Streamlit Cloud.

USDA PSD API: https://apps.fas.usda.gov/psdonline/api/psd/
Country code for Brazil: BR
Attribute ID 176 = Exports (1000 MT)
"""

import requests
import pandas as pd
import json
import os
import time
from datetime import datetime

BASE_URL = "https://apps.fas.usda.gov/psdonline/api/psd"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; commodity-monitor/1.0)",
}

# USDA PSD commodity codes (confirmed via fas.usda.gov/data/production/commodity/<code>)
COMMODITIES = {
    "Soybeans": "2222000",
    "Corn":     "0440000",
    "Wheat":    "0410000",
    "Coffee":   "0711100",
    "Sugar":    "0613100",
    "Cocoa":    "0721100",
}

# Market years to fetch
YEARS = [2021, 2022, 2023, 2024]

# Attribute ID 176 = Exports (1000 MT) in PSD
EXPORT_ATTR_ID = 176

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def fetch_psd(commodity_code: str, year: int) -> list:
    """Fetch PSD data for Brazil, one commodity, one year."""
    url = f"{BASE_URL}/commodity/{commodity_code}/country/BR/year/{year}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"ERROR fetching {commodity_code} / {year}: {e}")
        return []


def get_export_value(records: list) -> float:
    """Extract export volume (1000 MT) from PSD records."""
    for rec in records:
        if rec.get("attributeId") == EXPORT_ATTR_ID:
            return float(rec.get("value", 0) or 0)
    return 0.0


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- Annual summary (Page 1 Overview) ---
    print("Fetching annual export summary from USDA PSD...")
    summary_rows = []

    for name, code in COMMODITIES.items():
        for year in YEARS:
            print(f"  {name} {year}...", end=" ")
            records = fetch_psd(code, year)
            volume = get_export_value(records)
            summary_rows.append({
                "Commodity":      name,
                "year":           year,
                "Exports (1000MT)": volume,
            })
            print(f"OK ({volume:,.0f} 1000 MT)")
            time.sleep(0.3)  # be polite to the API

    df_summary = pd.DataFrame(summary_rows)
    path_summary = os.path.join(DATA_DIR, "exports_summary.csv")
    df_summary.to_csv(path_summary, index=False)
    print(f"\nSaved: {path_summary} ({len(df_summary)} rows)")

    # --- By-country data ---
    # USDA PSD does not provide by-country breakdown for Brazil's exports.
    # We generate a simple placeholder so exports_by_country.csv always exists.
    # The Streamlit page 3 will show a note about data availability.
    print("\nGenerating exports_by_country.csv (USDA PSD does not provide by-country data)...")
    country_rows = []
    for name, code in COMMODITIES.items():
        for year in YEARS:
            country_rows.append({
                "commodity":     name,
                "year":          year,
                "Country":       "Brazil (total)",
                "Exports (USD)": 0,
                "Weight (kg)":   0,
            })

    df_country = pd.DataFrame(country_rows)
    path_country = os.path.join(DATA_DIR, "exports_by_country.csv")
    df_country.to_csv(path_country, index=False)
    print(f"Saved: {path_country}")

    # --- Metadata ---
    meta = {"last_updated": datetime.utcnow().isoformat() + "Z", "source": "USDA PSD"}
    with open(os.path.join(DATA_DIR, "exports_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nDone. Last updated: {meta['last_updated']}")


if __name__ == "__main__":
    main()
