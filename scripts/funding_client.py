import requests
import pandas as pd
from datetime import datetime

BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"


def fetch_funding_rates(symbol="BTCUSDT", limit=30):
    """
    Fetch recent BTC perpetual funding rates from Binance Futures.
    Returns DataFrame with fundingTime, fundingRate
    """
    params = {
        "symbol": symbol,
        "limit": limit
    }

    r = requests.get(BINANCE_FUNDING_URL, params=params, timeout=20)
    r.raise_for_status()

    data = r.json()
    if not data:
        raise ValueError("No funding rate data returned")

    df = pd.DataFrame(data)
    df["fundingTime"] = pd.to_datetime(df["fundingTime"], unit="ms")
    df["fundingRate"] = pd.to_numeric(df["fundingRate"], errors="coerce")

    df = df.dropna().reset_index(drop=True)
    return df[["fundingTime", "fundingRate"]]


def classify_funding(df, threshold=0.01):
    """
    Classify funding regime based on latest funding rate.
    Returns: 'positive', 'neutral', or 'negative'
    """
    if df.empty:
        return "neutral"

    latest_rate = df.iloc[-1]["fundingRate"]

    if latest_rate > threshold:
        return "positive"
    elif latest_rate < -threshold:
        return "negative"
    else:
        return "neutral"


# --- Local test ---
if __name__ == "__main__":
    df = fetch_funding_rates()
    print(df.tail())

    print("\nFunding Regime:")
    print(classify_funding(df))