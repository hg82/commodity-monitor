"""
modules/exports.py
Brazilian export data from Comex Stat / MDIC
"""

import requests
import pandas as pd

NCM_GROUPS = {
    "Soybeans": ["12010000", "12080000", "23040000"],
    "Corn":     ["10059010", "10059090"],
    "Wheat":    ["10019900", "11010010"],
    "Coffee":   ["09011110", "09011190", "21011100"],
    "Sugar":    ["17011400", "17019900"],
    "Cocoa":    ["18010000", "18020000", "18031000"],
}

BASE_URL = "https://api-comexstat.mdic.gov.br/general"


def _payload(ncm_list, year, details):
    return {
        "yearStart": year,
        "yearEnd": year,
        "monthStart": 1,
        "monthEnd": 12,
        "monthDetail": False,
        "flow": "export",
        "typeOrder": 1,
        "typeForm": 1,
        "detailList": details,
        "filterList": [
            {
                "filter": "ncm",
                "values": ncm_list
            }
        ],
        "metricList": ["metricFOB"]
    }


def _request_data(ncm_list, year, details):

    try:

        response = requests.post(
            BASE_URL,
            json=_payload(ncm_list, year, details),
            timeout=30,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

        print("=" * 60)
        print("STATUS:", response.status_code)

        try:
            data = response.json()
        except Exception:
            print("RAW RESPONSE:")
            print(response.text[:1000])
            return []

        print("JSON KEYS:", list(data.keys()) if isinstance(data, dict) else type(data))

        if isinstance(data, dict):

            if "data" in data:

                if isinstance(data["data"], list):
                    return data["data"]

                if isinstance(data["data"], dict):

                    if "list" in data["data"]:
                        return data["data"]["list"]

            if "list" in data:
                return data["list"]

        elif isinstance(data, list):
            return data

        return []

    except Exception as e:

        print("COMEX ERROR:", str(e))
        return []


def _find_column(columns, keywords):

    for col in columns:
        col_lower = col.lower()

        for keyword in keywords:
            if keyword.lower() in col_lower:
                return col

    return None


def get_exports_by_commodity(commodity, year=2023):

    ncm_list = NCM_GROUPS.get(commodity)

    if not ncm_list:
        return pd.DataFrame()

    records = _request_data(
        ncm_list,
        year,
        ["country"]
    )

    if not records:
        print(f"No records found for {commodity}")
        return pd.DataFrame()

    df = pd.DataFrame(records)

    print("EXPORT COLUMNS:", df.columns.tolist())

    country_col = _find_column(
        df.columns,
        [
            "country",
            "pais",
            "nopais",
            "countryname"
        ]
    )

    fob_col = _find_column(
        df.columns,
        [
            "fob",
            "metricfob",
            "valor"
        ]
    )

    if not country_col or not fob_col:

        print("Country column:", country_col)
        print("FOB column:", fob_col)

        return pd.DataFrame()

    df = df[[country_col, fob_col]].copy()

    df.columns = [
        "Destination",
        "FOB Value (USD)"
    ]

    df["FOB Value (USD)"] = pd.to_numeric(
        df["FOB Value (USD)"],
        errors="coerce"
    )

    df = df.dropna()

    if df.empty:
        return pd.DataFrame()

    df = (
        df.groupby(
            "Destination",
            as_index=False
        )
        .sum()
        .sort_values(
            "FOB Value (USD)",
            ascending=False
        )
        .head(15)
    )

    df["FOB Value (USD)"] = df[
        "FOB Value (USD)"
    ].apply(
        lambda x: f"${x:,.0f}"
    )

    return df.reset_index(drop=True)


def get_annual_exports_summary(year=2023):

    rows = []

    for commodity, ncm_list in NCM_GROUPS.items():

        records = _request_data(
            ncm_list,
            year,
            ["country"]
        )

        if not records:

            print(
                f"No summary records for {commodity}"
            )

            continue

        df = pd.DataFrame(records)

        print(
            f"{commodity} columns:",
            df.columns.tolist()
        )

        fob_col = _find_column(
            df.columns,
            [
                "fob",
                "metricfob",
                "valor"
            ]
        )

        if not fob_col:

            print(
                f"FOB column not found for {commodity}"
            )

            continue

        df[fob_col] = pd.to_numeric(
            df[fob_col],
            errors="coerce"
        )

        total = df[fob_col].sum()

        rows.append(
            {
                "Commodity": commodity,
                "Exports (USD)": total,
                "Year": year
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:

        print("EXPORT SUMMARY EMPTY")

        return result

    result = result.sort_values(
        "Exports (USD)",
        ascending=False
    ).reset_index(drop=True)

    return result
