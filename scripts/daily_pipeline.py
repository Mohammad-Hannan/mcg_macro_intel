import json
from datetime import datetime

from scripts.risk_engine import compute_crs, compute_mrg
from scripts.overlay_engine import compute_overlay_signal
from scripts.signal_formatter import format_portfolio_signal
from scripts.signal_history_logger import log_daily_signal
from scripts.mrg_tracker import compute_delta_mrg, save_today_mrg
from scripts.mrg_tracker import load_history
from scripts.risk_regime import classify_risk_regime

from scripts.config.settings import DEFAULT_ACTION, REGIME_UNCLEAR
from scripts.logger import get_logger
logger = get_logger("daily_pipeline")

from scripts.btc_client import (
    fetch_btc_history,
    compute_moving_averages,
    compute_vol_regime,
    compute_shock_mode
)

from scripts.etf_client import (
    fetch_etf_flows,
    compute_flow_regime
)

from scripts.funding_client import (
    fetch_funding_rates,
    classify_funding
)

from scripts.fear_greed_client import (
    fetch_fear_greed,
    classify_tactical_bias
)

from scripts.pmi_client import (
    load_pmi_data,
    compute_pmi_metrics,
    classify_macro_regime
)

from scripts.output_writer import write_daily_output
from scripts.phase2.phase2_pipeline import run_phase2


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------

def refresh_data_if_needed(fetch_function, max_attempts=2):
    last_exception = None
    for attempt in range(max_attempts):
        try:
            return fetch_function()
        except Exception as e:
            last_exception = e
            logger.warning(f"Retry attempt {attempt + 1} failed: {e}")
    raise last_exception


def get_macro_regime():
    try:
        df = load_pmi_data()
        metrics = compute_pmi_metrics(df)

        if not metrics:
            return REGIME_UNCLEAR, None

        regime = classify_macro_regime(
            metrics["pmi_3m_avg"],
            metrics["pmi_trend"]
        )

        return regime, metrics

    except Exception as e:
        logger.warning(f"PMI error: {e}")
        return REGIME_UNCLEAR, None


# ---------------------------------------------------
# Main Pipeline
# ---------------------------------------------------

def run_daily_pipeline():

    logger.info("Starting daily pipeline")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    weekend_mode = datetime.utcnow().weekday() >= 5

    data_health = "healthy"
    health_warnings = []

    # ---------------- BTC ----------------
try:
    btc_df = refresh_data_if_needed(fetch_btc_history)

except Exception as e:
    logger.error(f"BTC error: {e}")
    btc_df = None

if btc_df is not None and not btc_df.empty:
    structure = compute_moving_averages(btc_df)
    vol_regime = compute_vol_regime(btc_df)
    shock_data = compute_shock_mode(btc_df)

    shock_mode = shock_data["shock_mode"]

else:
    logger.warning("BTC data unavailable — using safe defaults")

    structure = {
        "above_50dma": "unknown",
        "above_200dma": "unknown",
        "volatility": "unknown"
    }

    vol_regime = "unknown"

    shock_data = {
        "shock_mode": False,
        "pct_change_24h": 0,
        "intraday_range": 0
    }

    shock_mode = False

    # ---------------- ETF ----------------
    try:
        etf_df = refresh_data_if_needed(fetch_etf_flows)
        etf_flow_regime = compute_flow_regime(etf_df)
    except Exception as e:
        logger.warning(f"ETF error: {e}")
        etf_flow_regime = "mixed"
        data_health = "degraded"
        health_warnings.append("ETF failure")

    # ---------------- FUNDING ----------------
    try:
        funding_df = refresh_data_if_needed(fetch_funding_rates)
        funding_regime = classify_funding(funding_df)
    except Exception as e:
        logger.warning(f"Funding error: {e}")
        funding_regime = "neutral"

    # ---------------- PMI ----------------
    macro_regime, pmi_metrics = get_macro_regime()

    # ---------------- PHASE 2 ----------------
    try:
        phase2_data = run_phase2(
            macro_regime=macro_regime,
            intraday_range=shock_data["intraday_range"]
        )
    except Exception as e:
        logger.error(f"Phase II error: {e}")
        phase2_data = None
        data_health = "degraded"
        health_warnings.append("Phase II failure")

    # ---------------- FEAR & GREED ----------------
    try:
        fg_data = fetch_fear_greed()

        if fg_data:
            tactical_bias = classify_tactical_bias(fg_data["value"])
        else:
            tactical_bias = "TACTICAL_HOLD"

    except Exception as e:
        logger.warning(f"Fear & Greed failure: {e}")
        fg_data = None
        tactical_bias = "TACTICAL_HOLD"

    if weekend_mode and tactical_bias in ["TACTICAL_ADD_STRONG", "TACTICAL_ADD"]:
        tactical_bias = "TACTICAL_HOLD"

    # ---------------------------------------------------
    # RISK ENGINE
    # ---------------------------------------------------

    fear_value = fg_data["value"] if fg_data else None

    crs = compute_crs(
        above_50dma=structure["above_50dma"],
        above_200dma=structure["above_200dma"],
        volatility=vol_regime,
        fear_greed_value=fear_value,
        etf_flow_regime=etf_flow_regime,
        macro_regime=macro_regime
    )

    lrs = phase2_data["liquidity_regime"]["lrs"] if phase2_data else 0
    mrg = compute_mrg(crs, lrs)

    # ---------------- ΔMRG CALCULATION ----------------

    delta_mrg = compute_delta_mrg(mrg)

    save_today_mrg(mrg)

    # ---------------------------------------------------


    risk_regime = classify_risk_regime(mrg)

     # ---------------------------------------------------
    # OVERLAY ENGINE
    # ---------------------------------------------------

    close_column = None

    for col in btc_df.columns:
        if col.lower() in ["close", "price", "btc_price"]:
            close_column = col
            break

    if close_column is None:
        raise ValueError(f"No valid close/price column found in BTC dataframe")

    close_series = btc_df[close_column]

    overlay = compute_overlay_signal(
        mrg=mrg,
        close_series=close_series
    )

    portfolio_signal = format_portfolio_signal(
        mrg=mrg,
        overlay=overlay
    )

    history_df = load_history()

    mrg_history = history_df.tail(30).to_dict("records")

    # ---------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------

    output = {
        "date": today,
        "weekend_mode": weekend_mode,
        "data_health": data_health,
        "health_warnings": health_warnings,

        "risk_regime": risk_regime,

        "risk_engine": {
            "crs": crs,
            "lrs": lrs,
            "mrg": mrg
        },

        "mrg_change": delta_mrg,
        "mrg_history": mrg_history,

        "overlay": overlay,
        "phase2": phase2_data,
        "macro_regime": macro_regime,

        "shock": {
            "shock_mode": shock_mode,
            "pct_change_24h": shock_data.get("pct_change_24h"),
            "intraday_range": shock_data.get("intraday_range")
        },

        "portfolio_signal": portfolio_signal,

        "fear_greed": fg_data if fg_data else {
            "value": None,
            "classification": None,
            "source": None
        },

        "tactical_bias": tactical_bias,

        "btc_structure": {
            "above_50dma": structure["above_50dma"],
            "above_200dma": structure["above_200dma"],
            "volatility": vol_regime
        },

        "institutional_flows": {
            "etf_flow_regime": etf_flow_regime
        },

        "funding": {
            "funding_regime": funding_regime
        },

        "pmi": pmi_metrics if pmi_metrics else {
            "pmi_3m_avg": None,
            "pmi_trend": None,
            "macro_regime": macro_regime
        }
    }

    latest_close = close_series.iloc[-1]

    log_daily_signal(
        date=today,
        close_price=float(latest_close),
        crs=crs,
        lrs=lrs,
        mrg=mrg,
        overlay=overlay,
        portfolio_signal=portfolio_signal
    )

    path = write_daily_output(output)

    logger.info(f"MRG: {mrg}")
    logger.info(f"MRG Change: {delta_mrg}")
    logger.info(f"Overlay Exposure: {overlay['exposure_recommendation']}")
    logger.info(f"Output written to {path}")
    logger.info("Daily pipeline completed successfully")
    logger.info("PIPELINE FINISHED CLEANLY")


if __name__ == "__main__":
    run_daily_pipeline()