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


def _build_payload(ncm_list, year, details):
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
        "metricList":  ["metricFOB", "metricKG"],
    }


def get_exports_by_commodity(commodity, year=2023):
    ncm_list = NCM_GROUPS.get(commodity, [])
    if not ncm_list:
        return pd.DataFrame()
    try:
        payload = _build_payload(ncm_list, year, ["country"])
        resp = requests.post(BASE_URL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        lst = data.get("data", {}).get("list", [])
        if not lst:
            return pd.DataFrame()
        df = pd.DataFrame(lst)
        name_col = next((c for c in df.columns if "country" in c.lower() or "pais" in c.lower() or "nopais" in c.lower()), None)
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
        print("Error exports: " + str(e))
        return pd.DataFrame()


def get_annual_exports_summary(year=2023):
    rows = []
    for commodity, ncm_list in NCM_GROUPS.items():
        try:
            payload = _build_payload(ncm_list, year, [])
            resp = requests.post(BASE_URL, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            lst = data.get("data", {}).get("list", [])
            if lst:
                fob_col = next((k for k in lst[0] if "fob" in k.lower()), None)
                if fob_col:
                    total = sum(float(r.get(fob_col, 0)) for r in lst if r.get(fob_col))
                    rows.append({"Commodity": commodity, "Exports (USD)": total, "Year": year})
        except Exception as e:
            print("Error summary " + commodity + ": " + str(e))
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Exports (USD)", ascending=False).reset_index(drop=True)
    return df
