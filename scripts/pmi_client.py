import pandas as pd
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "ism_pmi.csv"


def load_pmi_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"PMI CSV not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    # Normalize headers
    df.columns = [c.strip().lower() for c in df.columns]

    if "period" not in df.columns or "pmi" not in df.columns:
        raise ValueError(
            f"CSV must contain 'period' and 'pmi' columns. Found: {df.columns.tolist()}"
        )

    df["period"] = pd.to_datetime(df["period"])
    df["pmi"] = pd.to_numeric(df["pmi"], errors="coerce")

    df = df.dropna().sort_values("period").reset_index(drop=True)
    return df


def compute_pmi_metrics(df):
    df["pmi_3m_avg"] = df["pmi"].rolling(3).mean()

    if len(df) < 4:
        return None

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    delta = latest["pmi_3m_avg"] - prev["pmi_3m_avg"]

    if delta >= 0.2:
        trend = "RISING"
    elif delta <= -0.2:
        trend = "FALLING"
    else:
        trend = "FLAT"

    return {
        "period": latest["period"].strftime("%Y-%m"),
        "pmi": round(latest["pmi"], 2),
        "pmi_3m_avg": round(latest["pmi_3m_avg"], 2),
        "pmi_trend": trend,
    }


def classify_macro_regime(pmi_3m_avg, trend):
    if pmi_3m_avg < 46 and trend == "FALLING":
        return "REGIME_CONTRACTION"
    elif 46 <= pmi_3m_avg < 50 and trend == "RISING":
        return "REGIME_EARLY_RECOVERY"
    elif 50 <= pmi_3m_avg < 54 and trend == "RISING":
        return "REGIME_MID_EXPANSION"
    elif pmi_3m_avg >= 54 and trend in ("FLAT", "FALLING"):
        return "REGIME_LATE_CYCLE"
    else:
        return "REGIME_UNCLEAR"


if __name__ == "__main__":
    df = load_pmi_data()
    metrics = compute_pmi_metrics(df)

    if not metrics:
        print("Not enough PMI data to compute regime.")
    else:
        regime = classify_macro_regime(
            metrics["pmi_3m_avg"], metrics["pmi_trend"]
        )

        print("PMI Period:", metrics["period"])
        print("PMI:", metrics["pmi"])
        print("PMI 3M Avg:", metrics["pmi_3m_avg"])
        print("PMI Trend:", metrics["pmi_trend"])
        print("Macro Regime:", regime)