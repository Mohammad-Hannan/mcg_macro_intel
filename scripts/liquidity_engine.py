import numpy as np
import pandas as pd


def compute_liquidity_stress(df):

    df = df.copy()

    score = pd.Series(0, index=df.index)

    # Volatility spike
    returns = df["Close"].pct_change()
    vol = returns.rolling(30).std()
    vol_z = (vol - vol.rolling(180).mean()) / vol.rolling(180).std()

    score += np.where(vol_z > 2, 10, 0)

    # Large drawdown acceleration
    dd = df["Close"] / df["Close"].cummax() - 1
    score += np.where(dd < -0.3, 10, 0)

    return score.clip(0, 20)