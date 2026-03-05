import os
import pandas as pd
from datetime import datetime

HISTORY_PATH = "data/mrg_history.csv"


def load_history():

    # If file doesn't exist, return empty structure
    if not os.path.exists(HISTORY_PATH):
        return pd.DataFrame(columns=["date", "mrg"])

    try:
        df = pd.read_csv(HISTORY_PATH)

        # If file exists but is empty
        if df.empty or "mrg" not in df.columns:
            return pd.DataFrame(columns=["date", "mrg"])

        return df

    except Exception:
        # Handles EmptyDataError and any corrupted CSV
        return pd.DataFrame(columns=["date", "mrg"])


def save_today_mrg(mrg):

    today = datetime.utcnow().strftime("%Y-%m-%d")

    df = load_history()

    new_row = pd.DataFrame([{
        "date": today,
        "mrg": mrg
    }])

    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(HISTORY_PATH, index=False)


def compute_delta_mrg(current_mrg):

    df = load_history()

    # First run case
    if len(df) == 0:
        return 0

    yesterday = df.iloc[-1]["mrg"]

    delta = current_mrg - yesterday

    return round(delta, 2)