import requests
import pandas as pd
import json, os, time
from datetime import datetime

BASE_URL = "https://apps.fas.usda.gov/OpenData/api/psd"
HEADERS = {"Accept": "application/json", "User-Agent": "commodity-monitor/1.0"}
COMMODITIES = {"Soybeans":"2222000","Corn":"0440000","Wheat":"0410000","Coffee":"0711100","Sugar":"0613100","Cocoa":"0721100"}
YEARS = [2021, 2022, 2023, 2024]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Source: USDA PSD")
    rows = []
    for name, code in COMMODITIES.items():
        for year in YEARS:
            print(f"  {name} {year}...", end=" ", flush=True)
            try:
                url = f"{BASE_URL}/commodity/{code}/country/BR/year/{year}"
                r = requests.get(url, headers=HEADERS, timeout=30)
                r.raise_for_status()
                records = r.json()
                volume = next((float(x.get("value",0) or 0) for x in records if x.get("attributeId")==176), 0.0)
                rows.append({"Commodity":name,"year":year,"Exports (1000MT)":volume})
                print(f"OK ({volume:,.0f})")
            except Exception as e:
                print(f"ERROR: {e}")
                rows.append({"Commodity":name,"year":year,"Exports (1000MT)":0})
            time.sleep(0.3)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "exports_summary.csv"), index=False)
    print(f"Saved {len(df)} rows")
    with open(os.path.join(DATA_DIR, "exports_meta.json"), "w") as f:
        json.dump({"last_updated": datetime.utcnow().isoformat()+"Z", "source":"USDA PSD"}, f)
    print("Done.")

if __name__ == "__main__":
    main()
