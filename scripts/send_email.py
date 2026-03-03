def build_email(data):
    import os

    # ==============================
    # SAFE EXTRACTION
    # ==============================

    date = data.get("date")
    macro = data.get("macro_regime")
    weekend_mode = data.get("weekend_mode", False)
    data_health = data.get("data_health", "unknown")
    warnings = data.get("health_warnings", [])
    dashboard_url = os.getenv("DASHBOARD_URL", "Dashboard link not configured")

    risk_engine = data.get("risk_engine", {})
    overlay = data.get("overlay", {})
    phase2 = data.get("phase2", {})
    portfolio = data.get("portfolio_signal", {})

    shock = data.get("shock", {})
    btc = data.get("btc_structure", {})
    flows = data.get("institutional_flows", {})
    funding = data.get("funding", {})
    pmi = data.get("pmi", {})
    fg = data.get("fear_greed", {})

    # ==============================
    # CORE SCORES
    # ==============================

    crs = risk_engine.get("crs")
    lrs = risk_engine.get("lrs")
    mrg = risk_engine.get("mrg")

    exposure = overlay.get("exposure_recommendation")
    liquidity_stress = phase2.get("liquidity_regime", {}).get("liquidity_stress")
    lpi = phase2.get("lpi")
    institutional_bias = phase2.get("institutional_bias")

    # ETF details
    etf_data = phase2.get("etf_flows", {})
    flow7 = etf_data.get("flow_7d")
    flow30 = etf_data.get("flow_30d")
    flow_accel = etf_data.get("flow_acceleration")

    # Derivatives
    derivatives = phase2.get("derivatives", {})
    funding_rate = derivatives.get("funding")
    basis = derivatives.get("basis_percent")
    oi = derivatives.get("open_interest")

    # Portfolio outputs
    allocation = portfolio.get("btc_allocation_target")
    risk_level = portfolio.get("risk_level")
    structural_regime = portfolio.get("structural_regime")
    action_guidance = portfolio.get("action_guidance")
    overlay_version = portfolio.get("overlay_version")

    tactical = data.get("tactical_bias")

    # ==============================
    # FORMATTERS
    # ==============================

    weekend_text = "Yes" if weekend_mode else "No"
    shock_text = "ACTIVE 🚨" if shock.get("shock_mode") else "Normal"

    warnings_text = ", ".join(warnings) if warnings else "None"

    if exposure is not None:
        exposure_text = f"{round(exposure * 100, 2)}%"
    else:
        exposure_text = "N/A"

    if basis is not None:
        basis_text = f"{round(basis * 100, 2)}%"
    else:
        basis_text = "N/A"

    if funding_rate is not None:
        funding_text = f"{round(funding_rate, 6)}"
    else:
        funding_text = "N/A"

    liquidity_text = "STRESS ⚠️" if liquidity_stress else "Stable"

    fg_value = fg.get("value", "N/A")
    fg_class = fg.get("classification", "N/A")

    # ==============================
    # SUBJECT
    # ==============================

    subject = f"MCG Overlay v2 — {allocation} BTC | MRG {mrg} | {date}"

    # ==============================
    # BODY
    # ==============================

    body = f"""
MCG INTELLIGENCE — DAILY SYSTEM REPORT
Date: {date}

==================================================
SYSTEM STATUS
==================================================
Data Health: {data_health.upper()}
Warnings: {warnings_text}
Weekend Mode: {weekend_text}

==================================================
PORTFOLIO ALLOCATION
==================================================
BTC Allocation Target: {allocation}
Overlay Exposure: {exposure_text}
Risk Level: {risk_level}
Structural Regime: {structural_regime}
Action Guidance: {action_guidance}
Overlay Version: {overlay_version}

==================================================
CORE RISK ENGINE
==================================================
CRS (Core Risk Score): {crs}
LRS (Liquidity Regime Score): {lrs}
MRG (Macro Risk Gauge): {mrg}

Liquidity Stress: {liquidity_text}
Shock Mode: {shock_text}

==================================================
PHASE 2 — LEVERAGE & LIQUIDITY
==================================================
LPI (Leverage Pressure Index): {lpi}
Institutional Bias: {institutional_bias}

Funding Rate: {funding_text}
Futures Basis: {basis_text}
Open Interest: {oi}

ETF 7d Flow: {flow7}M
ETF 30d Flow: {flow30}M
Flow Acceleration: {flow_accel}M

==================================================
MARKET STRUCTURE
==================================================
Above 50DMA: {btc.get('above_50dma')}
Above 200DMA: {btc.get('above_200dma')}
Volatility Regime: {btc.get('volatility')}

==================================================
SENTIMENT
==================================================
Fear & Greed: {fg_value} ({fg_class})
Tactical Bias: {tactical}

==================================================
MACRO CONTEXT
==================================================
PMI: {pmi.get('pmi')}
PMI 3M Avg: {pmi.get('pmi_3m_avg')}
PMI Trend: {pmi.get('pmi_trend')}

==================================================
LIVE DASHBOARD
==================================================
View full interactive dashboard:

{dashboard_url}

This link provides:
• Allocation history
• Risk engine breakdown
• Liquidity regime state
• Institutional flow data
• Full system transparency


==================================================
SYSTEM PRINCIPLES
==================================================
• Macro defines structural permission
• Liquidity stress modifies risk tolerance
• Institutional flows confirm regime
• Leverage pressure measures instability
• Exposure scales smoothly — not binary

This is a systematic decision-support overlay.
Not investment advice.
"""

    return subject, body