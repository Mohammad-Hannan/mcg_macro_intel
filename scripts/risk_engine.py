def compute_crs(
    above_50dma,
    above_200dma,
    volatility,
    fear_greed_value,
    etf_flow_regime,
    macro_regime
):

    # --- Force scalar values ---
    if hasattr(above_50dma, "item"):
        above_50dma = above_50dma.item()

    if hasattr(above_200dma, "item"):
        above_200dma = above_200dma.item()

    if hasattr(volatility, "item"):
        volatility = volatility.item()

    if hasattr(fear_greed_value, "item"):
        fear_greed_value = fear_greed_value.item()

    if hasattr(etf_flow_regime, "item"):
        etf_flow_regime = etf_flow_regime.item()

    if hasattr(macro_regime, "item"):
        macro_regime = macro_regime.item()

    score = 0
    """
    Cycle Risk Score (0–100)
    """

    score = 0

    # --------------------------
    # 1) Trend Risk (0–30)
    # --------------------------
    if above_200dma == "no":
        score += 15
    if above_50dma == "no":
        score += 10
    if above_200dma == "no" and above_50dma == "no":
        score += 5

    # --------------------------
    # 2) Sentiment Risk (0–20)
    # Extreme greed = risk
    # Extreme fear = opportunity (low risk)
    # --------------------------
    if fear_greed_value is not None:
        if fear_greed_value > 75:
            score += 20
        elif fear_greed_value > 60:
            score += 10
        elif fear_greed_value < 20:
            score -= 5  # fear reduces cycle top risk

    # --------------------------
    # 3) Institutional Flow (0–25)
    # --------------------------
    if etf_flow_regime == "negative":
        score += 15
    elif etf_flow_regime == "mixed":
        score += 5

    # --------------------------
    # 4) Volatility Regime (0–15)
    # --------------------------
    if volatility == "high":
        score += 10

    # --------------------------
    # 5) Macro Regime (0–10)
    # --------------------------
    if macro_regime != "REGIME_BULLISH":
        score += 5

    score = max(0, min(score, 100))

    return score


def compute_mrg(crs, lrs):
    """
    MCG Risk Gauge (0–100)
    Liquidity amplifies structural risk
    """

    lrs_norm = lrs / 20.0
    mrg = crs * (1 + (lrs_norm * 0.5))

    return min(round(mrg, 2), 100)