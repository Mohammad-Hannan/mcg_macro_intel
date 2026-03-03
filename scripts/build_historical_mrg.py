import pandas as pd
import numpy as np
import yfinance as yf

from scripts.risk_engine import compute_crs
from scripts.wyckoff_structure import compute_wyckoff_structure
from scripts.momentum_engine import compute_momentum_exhaustion
from scripts.liquidity_engine import compute_liquidity_stress


def compute_volatility_regime(df):
    returns = df["Close"].pct_change()
    vol = returns.rolling(30).std()
    vol_threshold = vol.quantile(0.75)

    return np.where(vol > vol_threshold, "high", "normal")


def build_historical_mrg(start="2018-01-01"):

    # -------------------------
    # 1) Download BTC Data
    # -------------------------
    btc = yf.download("BTC-USD", start=start)

    # Fix multi-index columns from yfinance
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = btc.columns.get_level_values(0)

    # -------------------------
    # 2) Structural Layer
    # -------------------------

    # Wyckoff structure
    wy = compute_wyckoff_structure(btc)
    btc = btc.merge(wy, left_index=True, right_index=True, how="left")
    btc["wy_score"] = btc["wy_score"].fillna(0)

    # Trend structure
    btc["above_50dma"] = np.where(
        btc["Close"] > btc["Close"].rolling(50).mean(), "yes", "no"
    )

    btc["above_200dma"] = np.where(
        btc["Close"] > btc["Close"].rolling(200).mean(), "yes", "no"
    )

    # -----------------------------------
    # 200DMA Regime Logic
    # -----------------------------------
    btc["dma200"] = btc["Close"].rolling(200).mean()
    btc["dma200_slope"] = btc["dma200"].diff()

    btc["bear_regime"] = np.where(
        (btc["Close"] < btc["dma200"]) & (btc["dma200_slope"] < 0),
        1,
        0
    )

    btc["vol_regime"] = compute_volatility_regime(btc)

    # RSI proxy for Fear & Greed
    delta = btc["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    btc["fear_greed"] = 100 - (100 / (1 + rs))

    # ETF proxy
    btc["etf_flow_regime"] = np.where(
        btc["above_200dma"] == "no", "negative", "positive"
    )

    btc["macro_regime"] = "REGIME_UNCLEAR"

    # -------------------------
    # 3) Momentum Engine
    # -------------------------
    btc["momentum_score"] = compute_momentum_exhaustion(btc)

    # -------------------------
    # 4) Liquidity Engine
    # -------------------------
    btc["liquidity_score"] = compute_liquidity_stress(btc)

    # -------------------------
    # 5) Drop warmup rows
    # -------------------------
    btc = btc.dropna().copy()

    # -------------------------
    # 6) Hybrid MRG Construction
    # -------------------------

    mrg_values = []

    for i in range(len(btc)):

        above_50 = str(btc["above_50dma"].iloc[i])
        above_200 = str(btc["above_200dma"].iloc[i])
        vol_reg = str(btc["vol_regime"].iloc[i])
        fg_value = float(btc["fear_greed"].iloc[i])
        etf_reg = str(btc["etf_flow_regime"].iloc[i])
        macro_reg = "REGIME_UNCLEAR"

        # Structural base (trend + macro proxy)
        base_crs = compute_crs(
            above_50dma=above_50,
            above_200dma=above_200,
            volatility=vol_reg,
            fear_greed_value=fg_value,
            etf_flow_regime=etf_reg,
            macro_regime=macro_reg
        )

        # Add Wyckoff structural layer
        structural = base_crs + float(btc["wy_score"].iloc[i])

        # Add Momentum exhaustion
        momentum = float(btc["momentum_score"].iloc[i])

        # Add Liquidity stress
        liquidity = float(btc["liquidity_score"].iloc[i])

        # Hybrid MRG
        mrg = structural + momentum + liquidity
        mrg = min(mrg, 100)

        mrg_values.append(mrg)

    btc["mrg"] = mrg_values

    return btc[["Close", "mrg"]]