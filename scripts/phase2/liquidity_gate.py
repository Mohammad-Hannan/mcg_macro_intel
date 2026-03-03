def liquidity_permission(macro_regime):
    """
    Macro defines permission
    """

    if macro_regime in ["EXPANSION", "REGIME_RISK_ON"]:
        return True

    return False