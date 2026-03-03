import os
import pandas as pd


HISTORY_PATH = "outputs/signal_history.csv"


def log_daily_signal(
    date: str,
    close_price: float,
    crs: float,
    lrs: float,
    mrg: float,
    overlay: dict,
    portfolio_signal: dict
):
    """
    Appends daily signal snapshot to historical CSV log.
    Creates file if it does not exist.
    """

    os.makedirs("outputs", exist_ok=True)

    row = {
        "date": date,
        "close_price": close_price,
        "crs": crs,
        "lrs": lrs,
        "mrg": mrg,
        "exposure": overlay.get("exposure_recommendation"),
        "bear_regime": overlay.get("bear_regime"),
        "risk_level": portfolio_signal.get("risk_level"),
        "structural_regime": portfolio_signal.get("structural_regime")
    }

    df_row = pd.DataFrame([row])

    if os.path.exists(HISTORY_PATH):
        df_existing = pd.read_csv(HISTORY_PATH)
        df_updated = pd.concat([df_existing, df_row], ignore_index=True)
    else:
        df_updated = df_row

    df_updated.to_csv(HISTORY_PATH, index=False)
    