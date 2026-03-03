import pandas as pd


def compute_institutional_bias(etf_df):
    """
    Computes 7D and 30D smoothed ETF flows
    Returns structured institutional state
    """

    if etf_df is None or len(etf_df) < 30:
        return {
            "institutional_bias": "NEUTRAL",
            "flow_7d": None,
            "flow_30d": None,
            "flow_acceleration": None
        }

    # Ensure sorted
    etf_df = etf_df.sort_values("Date")

    # Use correct column: Total
    etf_df["flow_7d"] = etf_df["Total"].rolling(7).sum()
    etf_df["flow_30d"] = etf_df["Total"].rolling(30).sum()

    latest = etf_df.iloc[-1]

    flow_7d = latest["flow_7d"]
    flow_30d = latest["flow_30d"]

    # Acceleration = short-term minus long-term
    flow_acceleration = flow_7d - flow_30d

    # Institutional Bias Logic
    if flow_7d > 0 and flow_30d > 0:
        bias = "ACCUMULATING"
    elif flow_7d < 0 and flow_30d < 0:
        bias = "DISTRIBUTING"
    else:
        bias = "NEUTRAL"

    return {
        "institutional_bias": bias,
        "flow_7d": round(flow_7d, 2),
        "flow_30d": round(flow_30d, 2),
        "flow_acceleration": round(flow_acceleration, 2)
    }