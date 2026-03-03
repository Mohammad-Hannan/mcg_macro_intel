def composite_state(lpi, lfs, institutional_bias, liquidity_ok):

    if lpi > 60 and lfs in ["STRESSED", "BREAKING"]:
        structure = "LEVERAGE_EXPANSION"

    elif lfs == "CLEANSED":
        structure = "POST_PANIC_RESET"

    else:
        structure = "NEUTRAL"

    permissions = {
        "allow_carry": lpi < 40 and liquidity_ok,
        "allow_vol_selling": lfs == "STABLE" and liquidity_ok,
        "favor_spot": institutional_bias == "ACCUMULATING" and liquidity_ok
    }

    return structure, permissions