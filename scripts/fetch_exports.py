"""
scripts/fetch_exports.py
USDA PSD API - Brazilian export data
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

COMMODITIES = {
    "Soybeans": "2222000",
    "Corn":     "0440000",
    "Wheat":    "0410000",
    "Coffee":   "0711100",
    "Sugar":    "0613100",
    "Cocoa":    "0721100",
}

YEARS = [2021, 2022, 2023, 2024]
EXPORT_ATTR_ID = 176
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def fetch_psd(commodity_code: str, year: int) -> list:
    url = f"{BASE_URL}/commodity/{commodity_code}/country/BR/year/{year}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"ERROR: {e}")
        return []


def get_export_value(records: list) -> float:
    for rec in records:
        if rec.get("attributeId") == EXPORT_ATTR_ID:
            return float(rec.get("value", 0) or 0)
    return 0.0


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Fetching from USDA PSD...")
    summary_rows = []

    for name, code in COMMODITIES.items():
        for year in YEARS:
            print(f"  {name} {year}...", end=" ", flush=True)
            records = fetch_psd(code, year)
            volume = get_export_value(records)
            summary_rows.append({
                "Commodity":        name,
                "year":             year,
                "Exports (1000MT)": volume,
            })
            print(f"OK ({volume:,.0f} 1000 MT)")
            time.sleep(0.3)

    df = pd.DataFrame(summary_rows)
    path = os.path.join(DATA_DIR, "exports_summary.csv")
    df.to_csv(path, index=False)
    print(f"\nSaved: {path} ({len(df)} rows)")

    meta = {"last_updated": datetime.utcnow().isoformat() + "Z", "source": "USDA PSD"}
    with open(os.path.join(DATA_DIR, "exports_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Done. {meta['last_updated']}")


if __name__ == "__main__":
    main()
