"""
modules/exports.py
Brazilian export data via Comex Stat / MDIC API
"""

import requests
import pandas as pd

API_URL = "https://api-comexstat.mdic.gov.br/general"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# NCM codes as integers (no leading zeros, no quotes)
# API requires integer values inside filters
NCM_MAP = {
    "Soybeans":     [1201001, 1202900],
    "Corn":         [10059010],
    "Wheat":        [10019900, 10011900],
    "Coffee":       [9011110, 9011200, 9012100],
    "Sugar":        [17011400, 17019900],
    "Cocoa":        [18010000, 18031000],
}

# Country code -> name mapping (top Brazil export destinations)
COUNTRY_NAMES = {
    "160": "China",
    "249": "United States",
    "160": "China",
    "76":  "Netherlands",
    "22":  "Germany",
    "32":  "Argentina",
    "56":  "Belgium",
    "124": "Japan",
    "410": "South Korea",
    "764": "Thailand",
    "504": "Morocco",
    "818": "Egypt",
    "682": "Saudi Arabia",
    "356": "India",
    "566": "Nigeria",
}


def _build_payload(ncm_codes: list, year: int, month_detail: bool = False,
                   details: list = None) -> dict:
    """Build the POST payload for the Comex Stat API."""
    return {
        "flow": "export",
        "monthDetail": month_detail,
        "period": {
            "from": f"{year}-01",
            "to":   f"{year}-12",
        },
        "filters": [
            {
                "filter": "ncm",
                "values": ncm_codes,  # must be list of integers
            }
        ],
        "details": details or ["country"],
        "metrics": ["metricFOB", "metricKG"],
    }


def get_exports_by_commodity(commodity: str, year: int) -> pd.DataFrame:
    """
    Returns top export destinations for a given commodity and year.
    Expected by app.py — Page 3 (Brazil Exports).

    Returns DataFrame with columns: Country, Exports (USD), Weight (kg)
    """
    ncm_codes = NCM_MAP.get(commodity)
    if not ncm_codes:
        return pd.DataFrame(columns=["Country", "Exports (USD)", "Weight (kg)"])

    payload = _build_payload(ncm_codes, year, month_detail=False, details=["country"])

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        rows = data.get("data", {}).get("list", [])

        if not rows:
            return pd.DataFrame(columns=["Country", "Exports (USD)", "Weight (kg)"])

        df = pd.DataFrame(rows)

        # Rename columns to friendly names
        rename = {}
        if "country" in df.columns:
            rename["country"] = "Country"
        if "metricFOB" in df.columns:
            rename["metricFOB"] = "Exports (USD)"
        if "metricKG" in df.columns:
            rename["metricKG"] = "Weight (kg)"

        df = df.rename(columns=rename)

        # Keep only relevant columns
        keep = [c for c in ["Country", "Exports (USD)", "Weight (kg)"] if c in df.columns]
        df = df[keep]

        # Sort by exports descending, top 20
        if "Exports (USD)" in df.columns:
            df = df.sort_values("Exports (USD)", ascending=False).head(20)

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"[exports.py] get_exports_by_commodity error ({commodity}, {year}): {e}")
        return pd.DataFrame(columns=["Country", "Exports (USD)", "Weight (kg)"])


def get_annual_exports_summary(year: int = 2023) -> pd.DataFrame:
    """
    Returns total exports per commodity for a given year.
    Expected by app.py — Page 1 (Overview) bar chart.

    Returns DataFrame with columns: Commodity, Exports (USD)
    """
    results = []

    for commodity_name, ncm_codes in NCM_MAP.items():
        # Summary query: no country breakdown, just totals
        payload = {
            "flow": "export",
            "monthDetail": False,
            "period": {
                "from": f"{year}-01",
                "to":   f"{year}-12",
            },
            "filters": [
                {
                    "filter": "ncm",
                    "values": ncm_codes,
                }
            ],
            "details": ["ncm"],
            "metrics": ["metricFOB"],
        }

        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()
            rows = data.get("data", {}).get("list", [])

            if rows:
                total_fob = sum(r.get("metricFOB", 0) for r in rows)
            else:
                total_fob = 0

            results.append({
                "Commodity": commodity_name,
                "Exports (USD)": total_fob,
            })

        except Exception as e:
            print(f"[exports.py] get_annual_exports_summary error ({commodity_name}): {e}")
            results.append({
                "Commodity": commodity_name,
                "Exports (USD)": 0,
            })

    df = pd.DataFrame(results)

    # Remove rows with zero exports (API may not have data for all commodities)
    df = df[df["Exports (USD)"] > 0].reset_index(drop=True)

    return df
