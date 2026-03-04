def build_email(data):

    date = data.get("date", "N/A")

    # ---------------- PORTFOLIO SIGNAL ----------------
    portfolio = data.get("portfolio_signal", {})

    allocation = portfolio.get("btc_allocation_target", "N/A")
    risk_level = portfolio.get("risk_level", "N/A")
    guidance = portfolio.get("action_guidance", "N/A")
    structural = portfolio.get("structural_regime", "N/A")

    # ---------------- RISK ENGINE ----------------
    risk = data.get("risk_engine", {})

    crs = risk.get("crs", "N/A")
    lrs = risk.get("lrs", "N/A")
    mrg = risk.get("mrg", "N/A")

    overlay = data.get("overlay", {})
    exposure = overlay.get("exposure_recommendation", "N/A")

    # ---------------- PHASE 2 ----------------
    phase2 = data.get("phase2", {})

    lpi = phase2.get("lpi", "N/A")
    inst_bias = phase2.get("institutional_bias", "N/A")

    liquidity = phase2.get("liquidity_regime", {})
    liquidity_stress = liquidity.get("liquidity_stress", False)

    derivatives = phase2.get("derivatives", {})
    funding = derivatives.get("funding", "N/A")
    basis = derivatives.get("basis_percent", "N/A")
    oi = derivatives.get("open_interest", "N/A")

    # ---------------- MARKET CONTEXT ----------------
    fg = data.get("fear_greed", {})
    fg_value = fg.get("value", "N/A")
    fg_class = fg.get("classification", "N/A")

    btc = data.get("btc_structure", {})
    above50 = btc.get("above_50dma", "N/A")
    above200 = btc.get("above_200dma", "N/A")
    vol = btc.get("volatility", "N/A")

    flows = data.get("institutional_flows", {})
    etf_regime = flows.get("etf_flow_regime", "N/A")

    pmi = data.get("pmi", {})
    pmi_val = pmi.get("pmi", "N/A")
    pmi_trend = pmi.get("pmi_trend", "N/A")

    shock = data.get("shock", {})
    shock_mode = shock.get("shock_mode", False)

    # ---------------- SUBJECT ----------------

    subject = f"MCG Intelligence — MRG {mrg} | {date}"

    # ---------------- BODY ----------------

    body = f"""
MCG INTELLIGENCE SYSTEM — DAILY UPDATE
Date: {date}

==================================================
PORTFOLIO SIGNAL
==================================================
BTC Allocation Target: {allocation}
Risk Level: {risk_level}
Action Guidance: {guidance}
Structural Regime: {structural}

==================================================
RISK ENGINE
==================================================
CRS: {crs}
LRS: {lrs}
MRG: {mrg}
Overlay Exposure: {exposure}

==================================================
DERIVATIVES & LIQUIDITY
==================================================
Funding Rate: {funding}
Open Interest: {oi}
Basis: {basis}

LPI: {lpi}
Institutional Bias: {inst_bias}
Liquidity Stress: {"YES" if liquidity_stress else "NO"}

==================================================
MARKET CONTEXT
==================================================
Fear & Greed: {fg_value} ({fg_class})

ETF Flow Regime: {etf_regime}

Volatility Regime: {vol}
Above 50DMA: {above50}
Above 200DMA: {above200}

PMI: {pmi_val}
PMI Trend: {pmi_trend}

Shock Mode: {"ACTIVE" if shock_mode else "Normal"}

==================================================
SYSTEM PRINCIPLES
==================================================
• Macro defines permission
• Market structure defines timing
• Sentiment accelerates — never overrides
• Shock logic activates independently

This is a decision-support system, not a trading bot.
"""

    return subject, body