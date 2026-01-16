def decide_action(
    macro_regime,
    above_50dma,
    above_200dma,
    vol_regime,
    etf_flow_regime,
    funding_regime,
):
    """
    Core MCG decision engine.
    Returns one of: ADD / HOLD / TRIM
    """

    # --- Macro gate (absolute priority) ---
    if macro_regime in ("REGIME_CONTRACTION", "REGIME_UNCLEAR"):
        return "HOLD"

    # --- Market structure ---
    structure_score = 0
    if above_50dma == "yes":
        structure_score += 1
    if above_200dma == "yes":
        structure_score += 2

    # --- Institutional flows ---
    flow_score = 0
    if etf_flow_regime == "positive":
        flow_score += 1
    elif etf_flow_regime == "negative":
        flow_score -= 1

    # --- Volatility penalty ---
    vol_penalty = -1 if vol_regime == "high" else 0

    # --- Funding (minor modifier) ---
    funding_mod = 0
    if funding_regime == "positive":
        funding_mod = -0.5
    elif funding_regime == "negative":
        funding_mod = 0.5

    total_score = structure_score + flow_score + vol_penalty + funding_mod

    # --- Decision thresholds ---
    if total_score >= 3 and macro_regime in (
        "REGIME_EARLY_RECOVERY",
        "REGIME_MID_EXPANSION",
    ):
        return "ADD"

    if total_score <= 0 and macro_regime == "REGIME_LATE_CYCLE":
        return "TRIM"

    return "HOLD"


# --- Local test ---
if __name__ == "__main__":
    print(
        decide_action(
            macro_regime="REGIME_MID_EXPANSION",
            above_50dma="yes",
            above_200dma="no",
            vol_regime="low",
            etf_flow_regime="negative",
            funding_regime="neutral",
        )
    )