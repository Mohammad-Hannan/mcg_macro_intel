import numpy as np


# ---------------------------------------------------
# Liquidity Regime Score (LRS)
# Scale: 0–20
# ---------------------------------------------------

def percentile_rank(value, series):
    if len(series) == 0:
        return 50

    series = np.array(series)
    return (np.sum(series < value) / len(series)) * 100


def compute_lrs(
    history,
    current_oi,
    oi_change,
    price_change,
    current_funding,
    intraday_range
):
    """
    Liquidity Regime Score (0–20)

    Components:
    A) OI Compression
    B) Funding Instability
    C) OI / Price Divergence
    D) Volatility Expansion
    """

    if history is None or history.empty:
        return {
            "lrs": 0,
            "liquidity_stress": False,
            "components": {}
        }

    components = {}

    # ---------------------------------------------------
    # A) OI Compression Stress (0–5)
    # ---------------------------------------------------

    oi_series = history["open_interest"].values

    if len(oi_series) > 0:
        max_oi_30 = np.max(oi_series[-30:]) if len(oi_series) >= 30 else np.max(oi_series)
        drawdown = (max_oi_30 - current_oi) / max_oi_30 if max_oi_30 != 0 else 0

        if drawdown > 0.20:
            oi_score = 5
        elif drawdown > 0.10:
            oi_score = 3
        else:
            oi_score = 0
    else:
        oi_score = 0

    components["oi_compression"] = oi_score

    # ---------------------------------------------------
    # B) Funding Instability (0–5)
    # ---------------------------------------------------

    funding_series = history["funding"].values
    funding_pct = percentile_rank(abs(current_funding), np.abs(funding_series))

    if funding_pct > 90:
        funding_score = 5
    elif funding_pct > 75:
        funding_score = 3
    else:
        funding_score = 0

    components["funding_instability"] = funding_score

    # ---------------------------------------------------
    # C) OI / Price Divergence (0–5)
    # ---------------------------------------------------

    divergence_score = 0

    if price_change > 0 and oi_change < 0:
        divergence_score = 3
    elif price_change < 0 and oi_change > 0:
        divergence_score = 3

    if abs(oi_change) > 0.03 and abs(price_change) > 0.02:
        divergence_score = 5

    components["oi_price_divergence"] = divergence_score

    # ---------------------------------------------------
    # D) Volatility Expansion (0–5)
    # ---------------------------------------------------

    if "intraday_range" in history.columns:
        range_series = history["intraday_range"].values
        avg_range = (
            np.mean(range_series[-30:])
            if len(range_series) >= 30
            else np.mean(range_series)
        )

        if avg_range != 0 and intraday_range > 2 * avg_range:
            vol_score = 5
        else:
            vol_score = 0
    else:
        vol_score = 0

    components["volatility_expansion"] = vol_score

    # ---------------------------------------------------
    # Final Score
    # ---------------------------------------------------

    lrs = int(oi_score + funding_score + divergence_score + vol_score)
    liquidity_stress = bool(lrs >= 10)

    components = {k: int(v) for k, v in components.items()}

    return {
        "lrs": lrs,
        "liquidity_stress": liquidity_stress,
        "components": components
    }