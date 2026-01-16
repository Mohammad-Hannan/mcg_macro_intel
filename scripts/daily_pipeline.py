import json
from datetime import datetime

# Constants
from config.settings import (
    DEFAULT_ACTION,
    REGIME_UNCLEAR
)

# Logger
from scripts.logger import get_logger
logger = get_logger("daily_pipeline")

# Core BTC modules
from scripts.btc_client import (
    fetch_btc_history,
    compute_moving_averages,
    compute_vol_regime
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


def get_macro_regime():
    """PMI-backed macro regime with safe default"""
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
        logger.warning(f"PMI error, defaulting macro regime: {e}")
        return REGIME_UNCLEAR, None


def run_daily_pipeline():
    logger.info("Starting daily pipeline")
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # --- BTC Structure ---
    try:
        btc_df = fetch_btc_history()
        structure = compute_moving_averages(btc_df)
        vol_regime = compute_vol_regime(btc_df)
    except Exception as e:
        logger.error(f"BTC structure error: {e}")
        structure = {
            "above_50dma": "no",
            "above_200dma": "no"
        }
        vol_regime = "high"

    # --- ETF Flows ---
    try:
        etf_df = fetch_etf_flows()
        etf_flow_regime = compute_flow_regime(etf_df)
    except Exception as e:
        logger.warning(f"ETF flow error: {e}")
        etf_flow_regime = "mixed"

    # --- Funding ---
    try:
        funding_df = fetch_funding_rates()
        funding_regime = classify_funding(funding_df)
    except Exception as e:
        logger.warning(f"Funding error: {e}")
        funding_regime = "neutral"

    # --- PMI / Macro ---
    macro_regime, pmi_metrics = get_macro_regime()

    # --- Decision Engine ---
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

    # --- Final Output ---
    output = {
        "date": today,
        "macro_regime": macro_regime,
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