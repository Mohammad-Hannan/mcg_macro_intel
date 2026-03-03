import numpy as np
import pandas as pd


def compute_momentum_exhaustion(df):

    df = df.copy()

    score = pd.Series(0, index=df.index)

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Extreme RSI
    score += np.where(rsi > 80, 10, 0)

    # 8-week acceleration
    roc_8 = df["Close"].pct_change(56)
    roc_prev = df["Close"].pct_change(112)

    score += np.where((roc_8 > 0.6) & (roc_8 > roc_prev), 5, 0)

    # Z-score stretch
    mean_2y = df["Close"].rolling(504).mean()
    std_2y = df["Close"].rolling(504).std()
    z = (df["Close"] - mean_2y) / std_2y

    score += np.where(z > 2.5, 5, 0)

    return score.clip(0, 20)