import pandas as pd
from pathlib import Path


# Path to the manually maintained ETF flow CSV
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "btc_etf_flows.csv"


def fetch_etf_flows():
    """
    Load BTC ETF flows from a local CSV file.
    Phase 1 design: manual-friendly, reliable, non-breaking.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"ETF flow CSV not found at expected path:\n{DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    # Normalize columns
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

    # Drop bad rows
    df = df.dropna(subset=["Date", "Total"])

    # Sort oldest → newest
    df = df.sort_values("Date").reset_index(drop=True)

    return df


def compute_flow_regime(df, window=7):
    """
    Classify ETF flow regime using the last N trading days.
    """

    if len(df) < window:
        return "mixed"

    recent = df.tail(window)
    avg_flow = recent["Total"].mean()

    if avg_flow > 0:
        return "positive"
    elif avg_flow < 0:
        return "negative"
    else:
        return "mixed"


if __name__ == "__main__":
    df = fetch_etf_flows()

    print("\nLatest ETF flow rows:")
    print(df.tail())

    regime = compute_flow_regime(df)
    print("\nETF Flow Regime:", regime)