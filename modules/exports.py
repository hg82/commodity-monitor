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


def _extract_list(response_json):
    """
    Tenta encontrar a lista de registros
    independentemente da estrutura retornada.
    """

    if isinstance(response_json, list):
        return response_json

    if not isinstance(response_json, dict):
        return []

    if "data" in response_json:

        if isinstance(response_json["data"], list):
            return response_json["data"]

        if (
            isinstance(response_json["data"], dict)
            and "list" in response_json["data"]
        ):
            return response_json["data"]["list"]

    return []


def _find_fob_column(columns):

    candidates = [
        "metricFOB",
        "fob",
        "vlFob",
        "valorFob"
    ]

    for col in columns:
        if any(x.lower() in col.lower() for x in candidates):
            return col

    return None


def _find_country_column(columns):

    candidates = [
        "country",
        "countryname",
        "nopais",
        "coPais",
        "pais"
    ]

    for col in columns:
        if any(x.lower() in col.lower() for x in candidates):
            return col

    return None


def get_exports_by_commodity(commodity, year=2023):

    ncm_list = NCM_GROUPS.get(commodity)

    if not ncm_list:
        return pd.DataFrame()

    try:

        response = requests.post(
            BASE_URL,
            json=_payload(ncm_list, year, ["country"]),
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        records = _extract_list(data)

        if not records:
            print(f"No records for {commodity}")
            print(data)
            return pd.DataFrame()

        df = pd.DataFrame(records)

        country_col = _find_country_column(df.columns)
        fob_col = _find_fob_column(df.columns)

        if not country_col or not fob_col:
            print("Columns returned:")
            print(df.columns.tolist())
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

        df = (
            df.groupby("Destination", as_index=False)
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

    except Exception as e:

        print(
            f"Error loading exports for {commodity}: {e}"
        )

        return pd.DataFrame()


def get_annual_exports_summary(year=2023):

    rows = []

    for commodity, ncm_list in NCM_GROUPS.items():

        try:

            response = requests.post(
                BASE_URL,
                json=_payload(
                    ncm_list,
                    year,
                    ["country"]
                ),
                timeout=30
            )

            response.raise_for_status()

            data = response.json()
            records = _extract_list(data)

            if not records:
                print(f"No summary data for {commodity}")
                continue

            df = pd.DataFrame(records)

            fob_col = _find_fob_column(df.columns)

            if not fob_col:
                print(
                    f"FOB column not found for {commodity}"
                )
                print(df.columns.tolist())
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

        except Exception as e:

            print(
                f"Summary error for {commodity}: {e}"
            )

    result = pd.DataFrame(rows)

    if not result.empty:

        result = result.sort_values(
            "Exports (USD)",
            ascending=False
        ).reset_index(drop=True)

    return result
