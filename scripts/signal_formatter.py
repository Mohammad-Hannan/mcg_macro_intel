# ---------------------------------------------------
# MCG Signal Formatter
# Converts raw overlay output into client-facing signal
# ---------------------------------------------------

OVERLAY_VERSION = "MCG Overlay v2"


def format_portfolio_signal(mrg: float, overlay: dict):
    """
    Converts raw MRG + overlay output into
    product-facing portfolio guidance.

    Inputs:
        mrg      : Macro Risk Gauge (0–100)
        overlay  : output dict from compute_overlay_signal()

    Returns:
        dict containing:
            - btc_allocation_target (str)
            - risk_level (str)
            - action_guidance (str)
            - structural_regime (str)
            - overlay_version (str)
    """

    if overlay is None or overlay.get("exposure_recommendation") is None:
        return {
            "btc_allocation_target": None,
            "risk_level": "UNKNOWN",
            "action_guidance": "Insufficient data.",
            "structural_regime": "UNKNOWN",
            "overlay_version": OVERLAY_VERSION
        }

    exposure = overlay["exposure_recommendation"]
    bear_regime = overlay["bear_regime"]
    regime_state = overlay["regime_state"]

    allocation_percent = round(exposure * 100)

    # ---------------------------------------------------
    # Risk Level Interpretation
    # ---------------------------------------------------

    if mrg >= 85:
        risk_level = "Severe"
        action = "Reduce exposure aggressively. Capital preservation priority."
    elif mrg >= 70:
        risk_level = "High"
        action = "Trim exposure. Avoid adding risk."
    elif mrg >= 50:
        risk_level = "Elevated"
        action = "Maintain allocation. No aggressive positioning."
    elif mrg <= 30:
        risk_level = "Low"
        action = "Favorable risk/reward. Gradual accumulation permitted."
    else:
        risk_level = "Moderate"
        action = "Neutral positioning appropriate."

    # ---------------------------------------------------
    # Structural Regime
    # ---------------------------------------------------

    if bear_regime:
        structural_regime = "Structural Bear Regime (200DMA Downtrend)"
    else:
        structural_regime = "Neutral / Structural Uptrend"

    return {
        "btc_allocation_target": f"{allocation_percent}%",
        "risk_level": risk_level,
        "action_guidance": action,
        "structural_regime": structural_regime,
        "overlay_version": OVERLAY_VERSION
    }