import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", "config.env"))

FRED_API_KEY = os.getenv("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

def fetch_fred_series(series_id, start_date="2023-01-01"):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    observations = data.get("observations", [])
    df = pd.DataFrame(observations)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df

if __name__ == "__main__":
    print("Testing FRED API…")
    for sid in ["DGS10", "M2SL", "WALCL", "RRPONTSYD"]:
        print(f"\nFetching {sid}…")
        df = fetch_fred_series(sid)
        print(df.tail())