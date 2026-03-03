from datetime import datetime

from scripts.phase2.leverage_engine import compute_lpi, compute_lfs
from scripts.phase2.institutional_engine import compute_institutional_bias
from scripts.phase2.liquidity_gate import liquidity_permission
from scripts.phase2.composite_engine import composite_state
from scripts.phase2.derivatives_state import load_history, save_today
from scripts.phase2.liquidity_regime import compute_lrs

from scripts.phase2.derivatives_client import (
    fetch_funding_rate,
    fetch_open_interest,
    fetch_futures_price,
    fetch_spot_price,
    compute_basis
)

from scripts.etf_client import fetch_etf_flows


def run_phase2(macro_regime, intraday_range):

    # ---------------- LIVE DERIVATIVES DATA ----------------

    funding = fetch_funding_rate()
    open_interest = fetch_open_interest()
    futures_price = fetch_futures_price()
    spot_price = fetch_spot_price()
    basis = compute_basis(futures_price, spot_price)

    price = spot_price

    # ---------------- LOAD HISTORY ----------------

    history = load_history()

    if history is not None and not history.empty:

        previous = history.iloc[-1]

        funding_delta = funding - previous.get("funding", 0)

        prev_oi = previous.get("open_interest", 0)
        if prev_oi != 0:
            oi_change = (open_interest - prev_oi) / prev_oi
        else:
            oi_change = 0

        previous_price = (
            previous.get("price")
            or previous.get("close")
            or previous.get("Close")
        )

        if previous_price and previous_price != 0:
            price_change = (price - previous_price) / previous_price
        else:
            price_change = 0

        basis_delta = basis - previous.get("basis", 0)

    else:
        funding_delta = 0
        oi_change = 0
        price_change = 0
        basis_delta = 0

    # ---------------- SAVE TODAY SNAPSHOT ----------------

    save_today({
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "funding": funding,
        "open_interest": open_interest,
        "price": price,
        "basis": basis,
        "oi_change": oi_change
    })

    # ---------------- LEVERAGE ENGINE ----------------

    lpi = compute_lpi(
        funding=funding,
        funding_delta=funding_delta,
        basis=basis,
        basis_delta=basis_delta,
        open_interest=open_interest,
        history=history
    )

    lfs = compute_lfs(
        oi_change=oi_change,
        price_change=price_change,
        history=history
    )

    # ---------------- ETF / INSTITUTIONAL ----------------

    etf_df = fetch_etf_flows()
    inst_data = compute_institutional_bias(etf_df)
    institutional_bias = inst_data["institutional_bias"]

    # ---------------- LIQUIDITY PERMISSION ----------------

    liquidity_ok = liquidity_permission(macro_regime)

    # ---------------- COMPOSITE STATE ----------------

    structure, permissions = composite_state(
        lpi,
        lfs,
        institutional_bias,
        liquidity_ok
    )

    # ---------------- LIQUIDITY REGIME SCORE ----------------

    lrs_data = compute_lrs(
        history=history,
        current_oi=open_interest,
        oi_change=oi_change,
        price_change=price_change,
        current_funding=funding,
        intraday_range=intraday_range
    )

    # ---------------- RETURN ----------------

    return {
        "lpi": lpi,
        "lfs": lfs,
        "institutional_bias": institutional_bias,
        "liquidity_regime": lrs_data,
        "etf_flows": {
            "flow_7d": inst_data["flow_7d"],
            "flow_30d": inst_data["flow_30d"],
            "flow_acceleration": inst_data["flow_acceleration"]
        },
        "derivatives": {
            "funding": funding,
            "funding_delta": funding_delta,
            "basis_percent": basis,
            "basis_delta": basis_delta,
            "open_interest": open_interest,
            "oi_change": oi_change,
            "price_change": price_change
        },
        "liquidity_ok": liquidity_ok,
        "market_structure": structure,
        "permissions": permissions
    }