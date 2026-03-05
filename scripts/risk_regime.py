def classify_risk_regime(mrg):

    if mrg < 30:
        return "RISK_ON"

    if mrg < 50:
        return "NEUTRAL"

    if mrg < 70:
        return "ELEVATED"

    return "CRISIS"