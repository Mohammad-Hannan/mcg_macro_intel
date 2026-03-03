import numpy as np


# ---------------------------------------------------
# Utility: Percentile Rank
# ---------------------------------------------------

def percentile_rank(value, series):
    if len(series) == 0:
        return 50

    return (np.sum(series < value) / len(series)) * 100


# ---------------------------------------------------
# LPI — Leverage Pressure Index (0–100)
# ---------------------------------------------------

def compute_lpi(
    funding,
    funding_delta,
    basis,
    basis_delta,
    open_interest,
    history
):
    """
    Leverage Pressure Index (0–100)
    Percentile-based intelligence including OI.
    """

    if history is None or history.empty:
        return 50

    funding_series = history["funding"].values
    basis_series = history["basis"].values
    oi_series = history["open_interest"].values

    funding_pct = percentile_rank(funding, funding_series)
    basis_pct = percentile_rank(basis, basis_series)
    oi_pct = percentile_rank(open_interest, oi_series)

    # Acceleration component
    acceleration_score = 50
    if funding_delta > 0 and basis_delta > 0:
        acceleration_score = 70
    elif funding_delta < 0 and basis_delta < 0:
        acceleration_score = 30

    lpi = (
        0.4 * funding_pct +
        0.3 * basis_pct +
        0.2 * oi_pct +
        0.1 * acceleration_score
    )

    return round(lpi, 2)

# ---------------------------------------------------
# LFS — Leverage Fragility Score (Percentile Model)
# ---------------------------------------------------

def compute_lfs(oi_change, price_change, history=None):
    """
    Percentile-based fragility detection.
    Detects leverage expansion into weak price action.
    """

    # Fallback if no usable history
    if history is None or len(history) < 20:
        if oi_change > 0.02 and price_change <= 0:
            return "STRESSED"
        if oi_change < -0.02 and price_change < 0:
            return "CLEANSED"
        return "STABLE"

    # Extract OI percentile distribution
    oi_series = history["oi_change"].dropna().values

    # Compute price_change distribution from stored prices
    if "price" in history.columns:
        price_series = history["price"].pct_change().dropna().values
    else:
        price_series = np.array([])

    # If we somehow lack data, fallback
    if len(oi_series) == 0 or len(price_series) == 0:
        return "STABLE"

    oi_pct = percentile_rank(oi_change, oi_series)
    price_pct = percentile_rank(price_change, price_series)

    # --- FRAGILITY LOGIC ---

    if oi_pct > 80 and price_pct < 40:
        return "BREAKING"

    if oi_pct > 65 and price_pct < 50:
        return "STRESSED"

    if oi_pct < 25 and price_pct < 40:
        return "CLEANSED"

    if oi_pct > 60 and price_pct > 60:
        return "EXPANSION"

    return "STABLE"