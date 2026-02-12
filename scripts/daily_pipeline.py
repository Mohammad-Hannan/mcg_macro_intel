import json
from datetime import datetime

# Constants
from scripts.config.settings import DEFAULT_ACTION, REGIME_UNCLEAR

# Logger
from scripts.logger import get_logger
logger = get_logger("daily_pipeline")

# Core BTC modules
from scripts.btc_client import (
    fetch_btc_history,
    compute_moving_averages,
    compute_vol_regime,
    compute_shock_mode
)

# ETF flows
from scripts.etf_client import (
    fetch_etf_flows,
    compute_flow_regime
)

# Funding
from scripts.funding_client import (
    fetch_funding_rates,
    classify_funding
)

# Fear & Greed
from scripts.fear_greed_client import (
    fetch_fear_greed,
    classify_tactical_bias
)

# Decision engine
from scripts.decision_engine import decide_action

# PMI / Macro
from scripts.pmi_client import (
    load_pmi_data,
    compute_pmi_metrics,
    classify_macro_regime
)

# Output writer
from scripts.output_writer import write_daily_output



def refresh_data_if_needed(fetch_function, max_attempts=2):
    """
    Attempts to refetch data up to max_attempts.
    Returns fetched data or raises last exception.
    """
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


def run_daily_pipeline():

    logger.info("Starting daily pipeline")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    weekend_mode = datetime.utcnow().weekday() >= 5

    data_health = "healthy"
    health_warnings = []

    # ---------------- BTC ----------------
    try:
        btc_df = refresh_data_if_needed(fetch_btc_history)
        structure = compute_moving_averages(btc_df)
        vol_regime = compute_vol_regime(btc_df)
        shock_data = compute_shock_mode(btc_df)
        shock_mode = shock_data["shock_mode"]

    except Exception as e:
        logger.error(f"BTC error: {e}")
        structure = {"above_50dma": "no", "above_200dma": "no"}
        vol_regime = "high"
        shock_mode = False
        shock_data = {
            "pct_change_24h": None,
            "intraday_range": None
        }
        data_health = "degraded"
        health_warnings.append("BTC failure")

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

    # ---------------- FEAR & GREED ----------------
    fg_data = None
    tactical_bias = "TACTICAL_HOLD"

    try:
        fg_data = fetch_fear_greed()
        logger.info(f"FG RAW DATA: {fg_data}")

        if fg_data and fg_data.get("value") is not None:
            tactical_bias = classify_tactical_bias(fg_data["value"])
        else:
            health_warnings.append("Fear & Greed returned empty")

    except Exception as e:
        logger.warning(f"Fear & Greed failure: {e}")
        health_warnings.append("Fear & Greed API unreachable")

    # Weekend soft gating
    if weekend_mode and tactical_bias in ["TACTICAL_ADD_STRONG", "TACTICAL_ADD"]:
        tactical_bias = "TACTICAL_HOLD"


    # -------- FINAL DATA HEALTH GUARD --------
    # ---------------- HARD DATA HEALTH GUARD ----------------
    if data_health != "healthy":
        logger.error("Data health check failed — aborting signal generation")

        output = {
            "date": today,
            "status": "DATA_INVALID",
            "data_health": data_health,
            "health_warnings": health_warnings,
            "message": "Signal generation aborted due to stale or failed data sources."
        }

        path = write_daily_output(output)

        logger.error(f"Output written with DATA_INVALID status to {path}")
        return
    # ---------------- DECISION ENGINE ----------------
    try:
        final_action = decide_action(
            macro_regime=macro_regime,
            above_50dma=structure["above_50dma"],
            above_200dma=structure["above_200dma"],
            vol_regime=vol_regime,
            etf_flow_regime=etf_flow_regime,
            funding_regime=funding_regime
        )
    except Exception as e:
        logger.error(f"Decision engine error: {e}")
        final_action = DEFAULT_ACTION

    # ---------------- OUTPUT ----------------
    output = {
        "date": today,
        "weekend_mode": weekend_mode,
        "data_health": data_health,
        "health_warnings": health_warnings,
        "macro_regime": macro_regime,
        "shock": {
            "shock_mode": shock_mode,
            "pct_change_24h": shock_data.get("pct_change_24h"),
            "intraday_range": shock_data.get("intraday_range")
        },
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
        },
        "final_action": final_action
    }

    path = write_daily_output(output)

    logger.info(f"Final action: {final_action}")
    logger.info(f"Output written to {path}")
    logger.info("Daily pipeline completed successfully")


if __name__ == "__main__":
    run_daily_pipeline()