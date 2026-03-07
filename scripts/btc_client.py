import requests
import pandas as pd
import numpy as np
from datetime import datetime

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"


def fetch_btc_history(days=365):
    """
    Fetch daily BTC price history from CoinGecko.
    Returns DataFrame with columns: date, price
    """

    params = {
        "vs_currency": "usd",
        "days": days
    }

    for attempt in range(3):
        try:
            r = requests.get(COINGECKO_URL, params=params, timeout=20)
            r.raise_for_status()

            data = r.json().get("prices", [])
            if not data:
                raise ValueError("No BTC price data returned from CoinGecko")

            df = pd.DataFrame(data, columns=["timestamp", "price"])
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["price"] = pd.to_numeric(df["price"], errors="coerce")

            df = df.dropna().reset_index(drop=True)
            return df[["date", "price"]]

        except Exception as e:
            if attempt == 2:
                raise e

            logger.warning(f"CoinGecko BTC retry {attempt+1} failed: {e}")
            time.sleep(5)


def compute_moving_averages(df):
    """
    Compute 50DMA / 200DMA and determine price position.
    """
    df = df.copy()

    df["ma50"] = df["price"].rolling(window=50).mean()
    df["ma200"] = df["price"].rolling(window=200).mean()

    latest = df.iloc[-1]

    return {
        "latest_price": round(latest["price"], 2),
        "ma50": round(latest["ma50"], 2) if not np.isnan(latest["ma50"]) else None,
        "ma200": round(latest["ma200"], 2) if not np.isnan(latest["ma200"]) else None,
        "above_50dma": "yes" if latest["price"] > latest["ma50"] else "no",
        "above_200dma": "yes" if latest["price"] > latest["ma200"] else "no",
    }


def compute_realized_volatility(df, window=30):
    """
    Compute annualized realized volatility using log returns.
    """
    df = df.copy()
    df["log_return"] = np.log(df["price"] / df["price"].shift(1))

    vol = df["log_return"].tail(window).std()
    if pd.isna(vol):
        return None

    # Annualize (crypto trades ~365 days)
    return float(vol * np.sqrt(365))


def compute_shock_mode(df):
    """
    Detect abnormal BTC market shock conditions.
    Returns:
        {
            "shock_mode": bool,
            "pct_change_24h": float,
            "intraday_range": float
        }
    """

    df = df.copy().dropna()

    if len(df) < 2:
        return {
            "shock_mode": False,
            "pct_change_24h": 0,
            "intraday_range": 0
        }

    # Latest and previous close
    last_price = df.iloc[-1]["price"]
    prev_price = df.iloc[-2]["price"]

    pct_change_24h = (last_price - prev_price) / prev_price

    # Intraday range using last 2 days (approximation)
    high = max(df.iloc[-1]["price"], df.iloc[-2]["price"])
    low = min(df.iloc[-1]["price"], df.iloc[-2]["price"])

    intraday_range = (high - low) / last_price


    shock_mode = False

    # -8% or worse
    if pct_change_24h <= -0.08:
        shock_mode = True

    # 7%+ intraday range
    if intraday_range >= 0.07:
        shock_mode = True

    return {
        "shock_mode": shock_mode,
        "pct_change_24h": pct_change_24h,
        "intraday_range": intraday_range
    }

def compute_vol_regime(df, threshold=0.80):
    """
    Classify BTC volatility regime.
    Returns: 'low' or 'high'
    """
    vol = compute_realized_volatility(df)

    if vol is None:
        return "low"  # conservative default

    if vol > threshold:
        return "high"
    else:
        return "low"


# --- Local test ---
if __name__ == "__main__":
    print("Fetching BTC history...")
    df = fetch_btc_history()
    print(df.tail())

    print("\nMarket structure:")
    structure = compute_moving_averages(df)
    print(structure)

    print("\nVolatility:")
    vol = compute_realized_volatility(df)
    print("30D Realized Vol:", vol)

    print("\nVolatility Regime:")
    print(compute_vol_regime(df))