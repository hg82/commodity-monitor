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
        "yearStart":   year,
        "yearEnd":     year,
        "monthStart":  1,
        "monthEnd":    12,
        "monthDetail": False,
        "flow":        "export",
        "typeOrder":   1,
        "typeForm":    1,
        "detailList":  details,
        "filterList":  [{"filter": "ncm", "values": ncm_list}],
        "metricList":  ["metricFOB"],
    }


def get_exports_by_commodity(commodity, year=2023):
    ncm_list = NCM_GROUPS.get(commodity, [])
    if not ncm_list:
        return pd.DataFrame()
    try:
        resp = requests.post(BASE_URL, json=_payload(ncm_list, year, ["country"]), timeout=15)
        resp.raise_for_status()
        lst = resp.json().get("data", {}).get("list", [])
        if not lst:
            return pd.DataFrame()
        df = pd.DataFrame(lst)
        name_col = next((c for c in df.columns if "country" in c.lower()), None)
        fob_col  = next((c for c in df.columns if "fob" in c.lower()), None)
        if not name_col or not fob_col:
            return pd.DataFrame()
        df = df[[name_col, fob_col]].copy()
        df.columns = ["Destination", "FOB Value (USD)"]
        df["FOB Value (USD)"] = pd.to_numeric(df["FOB Value (USD)"], errors="coerce")
        df = df.dropna().sort_values("FOB Value (USD)", ascending=False).head(15).reset_index(drop=True)
        df["FOB Value (USD)"] = df["FOB Value (USD)"].apply(lambda x: f"${x:,.0f}")
        return df
    except Exception as e:
        print("exports error: " + str(e))
        return pd.DataFrame()


def get_annual_exports_summary(year=2023):
    rows = []
    for commodity, ncm_list in NCM_GROUPS.items():
        try:
            resp = requests.post(BASE_URL, json=_payload(ncm_list, year, []), timeout=15)
