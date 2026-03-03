import pandas as pd
import numpy as np

from scripts.build_historical_mrg import build_historical_mrg


def backtest_mrg(start="2018-01-01", scale_divisor=120, transaction_cost=0.002):

    # -----------------------------------
    # Load Data
    # -----------------------------------
    df = build_historical_mrg(start=start).copy()

    # --- Daily returns ---
    df["returns"] = df["Close"].pct_change()

    # -----------------------------------
    # Smooth Exposure Scaling
    # -----------------------------------
    df["exposure"] = 1 - (df["mrg"] / float(scale_divisor))
    df["exposure"] = df["exposure"].clip(lower=0.3, upper=1.0)

    # Optional smoothing
    df["exposure"] = df["exposure"].rolling(2).mean().fillna(df["exposure"])

    # -----------------------------------
    # 200DMA Bear Regime Lock
    # -----------------------------------
    df["dma200"] = df["Close"].rolling(200).mean()
    df["dma200_slope"] = df["dma200"].diff()

    df["bear_regime"] = (
        (df["Close"] < df["dma200"]) &
        (df["dma200_slope"] < 0)
    ).astype(int)

    # Cap exposure during structural bear
    df.loc[df["bear_regime"] == 1, "exposure"] = np.minimum(
        df["exposure"], 0.6
    )

    # -----------------------------------
    # Transaction Cost Modeling
    # -----------------------------------
    df["exposure_change"] = df["exposure"].diff().abs().fillna(0)
    df["cost"] = df["exposure_change"] * transaction_cost

    # -----------------------------------
    # Strategy Returns
    # -----------------------------------
    df["strategy_returns"] = (
        df["returns"] * df["exposure"]
        - df["cost"]
    )

    # -----------------------------------
    # Cumulative Growth
    # -----------------------------------
    df["bh_curve"] = (1 + df["returns"]).cumprod()
    df["strategy_curve"] = (1 + df["strategy_returns"]).cumprod()

    # -----------------------------------
    # Performance Metrics
    # -----------------------------------
    total_years = (df.index[-1] - df.index[0]).days / 365

    bh_cagr = df["bh_curve"].iloc[-1] ** (1 / total_years) - 1
    strat_cagr = df["strategy_curve"].iloc[-1] ** (1 / total_years) - 1

    bh_max_dd = (df["bh_curve"] / df["bh_curve"].cummax() - 1).min()
    strat_max_dd = (df["strategy_curve"] / df["strategy_curve"].cummax() - 1).min()

    bh_vol = df["returns"].std() * np.sqrt(365)
    strat_vol = df["strategy_returns"].std() * np.sqrt(365)

    print("\n===== BACKTEST RESULTS =====")
    print(f"Period: {df.index[0].date()} → {df.index[-1].date()}")

    print("\n--- Buy & Hold ---")
    print(f"CAGR: {bh_cagr:.2%}")
    print(f"Max Drawdown: {bh_max_dd:.2%}")
    print(f"Volatility: {bh_vol:.2%}")

    print("\n--- MRG Strategy ---")
    print(f"CAGR: {strat_cagr:.2%}")
    print(f"Max Drawdown: {strat_max_dd:.2%}")
    print(f"Volatility: {strat_vol:.2%}")

    return df


def run_robustness_test():

    divisors = [100, 120, 150]

    for d in divisors:
        print(f"\n===== ROBUSTNESS TEST | Divisor = {d} =====")
        backtest_mrg(start="2018-01-01", scale_divisor=d, transaction_cost=0.002)


if __name__ == "__main__":
    run_robustness_test()