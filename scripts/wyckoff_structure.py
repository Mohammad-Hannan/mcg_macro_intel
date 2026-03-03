import numpy as np
import pandas as pd


def compute_wyckoff_structure(df, range_weeks=20):

    df = df.copy()

    # --- Weekly data ---
    weekly = df["Close"].resample("W").last()
    weekly_high = df["High"].resample("W").max()
    weekly_low = df["Low"].resample("W").min()
    weekly_vol = df["Volume"].resample("W").sum()

    w = pd.DataFrame({
        "close": weekly,
        "high": weekly_high,
        "low": weekly_low,
        "volume": weekly_vol
    }).dropna()

    # Range boundaries
    w["range_high"] = w["high"].rolling(range_weeks).max()
    w["range_low"] = w["low"].rolling(range_weeks).min()

    # Spread & volume ratios
    w["spread"] = w["high"] - w["low"]
    w["spread_ma"] = w["spread"].rolling(20).mean()

    w["vol_ma"] = w["volume"].rolling(20).mean()
    w["vol_ratio"] = w["volume"] / w["vol_ma"]

    # --- Distribution Signals ---

    # 1) Near top of range
    w["near_top"] = w["close"] > (w["range_high"] - (w["range_high"] - w["range_low"]) * 0.2)

    # 2) Churn: high volume + small spread
    w["churn"] = (w["vol_ratio"] > 2) & (w["spread"] < w["spread_ma"])

    w["distribution_churn"] = w["near_top"] & w["churn"]

    # 3) Weak breakout (UTAD proxy)
    w["breakout"] = w["close"] > w["range_high"].shift(1)
    w["weak_breakout"] = w["breakout"] & (w["vol_ratio"] < 1.1)

    # 4) Breakdown
    w["breakdown"] = w["close"] < w["range_low"].shift(1)

    # --- Scoring (0–30) ---
    w["wy_score"] = 0

    w.loc[w["distribution_churn"], "wy_score"] += 10
    w.loc[w["weak_breakout"], "wy_score"] += 10
    w.loc[w["breakdown"], "wy_score"] += 10

    # Clamp
    w["wy_score"] = w["wy_score"].clip(0, 30)

    return w[["wy_score"]]