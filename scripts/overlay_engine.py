import numpy as np


OVERLAY_VERSION = "MCG Overlay v2"


def compute_overlay_signal(
    mrg: float,
    close_series,
    scale_divisor: float = 120.0
):
    """
    Production Overlay Engine

    Inputs:
        mrg            : Latest MCG Risk Gauge value (0–100)
        close_series   : Pandas Series of recent BTC closing prices
        scale_divisor  : Scaling constant for exposure curve

    Returns:
        dict containing:
            - exposure_recommendation
            - bear_regime (bool)
            - regime_state (str)
            - overlay_version
    """

    if close_series is None or len(close_series) < 200:
        return {
            "exposure_recommendation": None,
            "bear_regime": None,
            "regime_state": "INSUFFICIENT_DATA",
            "overlay_version": OVERLAY_VERSION
        }

    # -----------------------------------
    # 1️⃣ Smooth Exposure Scaling
    # -----------------------------------
    exposure = 1 - (mrg / float(scale_divisor))

    # Clamp between 30% and 100%
    exposure = float(np.clip(exposure, 0.3, 1.0))

    # -----------------------------------
    # 2️⃣ 200DMA Bear Regime Lock
    # -----------------------------------
    dma200 = close_series.rolling(200).mean()
    dma200_slope = dma200.diff()

    latest_price = close_series.iloc[-1]
    latest_dma200 = dma200.iloc[-1]
    latest_slope = dma200_slope.iloc[-1]

    bear_regime = False

    if (
        latest_price < latest_dma200
        and latest_slope is not None
        and not np.isnan(latest_slope)
        and latest_slope < 0
    ):
        bear_regime = True
        exposure = min(exposure, 0.6)

    # -----------------------------------
    # 3️⃣ Risk State Label
    # -----------------------------------
    if mrg >= 85:
        regime_state = "SEVERE"
    elif mrg >= 70:
        regime_state = "HIGH"
    elif mrg >= 50:
        regime_state = "ELEVATED"
    else:
        regime_state = "LOW"

    return {
        "exposure_recommendation": round(exposure, 4),
        "bear_regime": bear_regime,
        "regime_state": regime_state,
        "overlay_version": OVERLAY_VERSION
    }