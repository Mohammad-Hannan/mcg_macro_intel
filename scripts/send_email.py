def build_email(data):

    # ---- Extract safely ----
    date = data.get("date")
    macro = data.get("macro_regime")
    final_action = data.get("final_action")
    weekend_mode = data.get("weekend_mode", False)
    data_health = data.get("data_health", "unknown")
    warnings = data.get("health_warnings", [])

    shock = data.get("shock", {})
    shock_mode = shock.get("shock_mode", False)
    pct_change = shock.get("pct_change_24h")
    intraday_range = shock.get("intraday_range")

    btc = data.get("btc_structure", {})
    flows = data.get("institutional_flows", {})
    funding = data.get("funding", {})
    pmi = data.get("pmi", {})
    fg = data.get("fear_greed", {})
    tactical = data.get("tactical_bias", "TACTICAL_HOLD")

    # ---- Formatting ----
    shock_text = "🚨 SHOCK MODE ACTIVE" if shock_mode else "Normal"
    weekend_text = "Yes" if weekend_mode else "No"

    if pct_change is not None:
        pct_change = f"{round(pct_change * 100, 2)}%"
    else:
        pct_change = "N/A"

    if intraday_range is not None:
        intraday_range = f"{round(intraday_range * 100, 2)}%"
    else:
        intraday_range = "N/A"

    fg_value = fg.get("value", "N/A")
    fg_class = fg.get("classification", "N/A")

    warnings_text = ", ".join(warnings) if warnings else "None"

    # ---- Subject ----
    subject = f"MCG Intelligence — {final_action} | {date}"

    # ---- Body ----
    body = f"""
MCG INTELLIGENCE SYSTEM — DAILY UPDATE
Date: {date}

==================================================
SYSTEM STATUS
==================================================
Data Health: {data_health.upper()}
Warnings: {warnings_text}

==================================================
CORE DECISION
==================================================
Final Action: {final_action}
Macro Regime: {macro}
Shock Mode: {shock_text}
Weekend Mode: {weekend_text}

24h Change: {pct_change}
Intraday Range: {intraday_range}

==================================================
BTC MARKET STRUCTURE
==================================================
Above 50DMA: {btc.get('above_50dma')}
Above 200DMA: {btc.get('above_200dma')}
Volatility Regime: {btc.get('volatility')}

==================================================
INSTITUTIONAL FLOWS
==================================================
ETF Flow Regime: {flows.get('etf_flow_regime')}
Funding Regime: {funding.get('funding_regime')}

==================================================
SENTIMENT OVERLAY
==================================================
Fear & Greed Index: {fg_value} ({fg_class})
Tactical Bias: {tactical}

==================================================
MACRO CONTEXT (PMI)
==================================================
PMI: {pmi.get('pmi')}
PMI 3M Average: {pmi.get('pmi_3m_avg')}
PMI Trend: {pmi.get('pmi_trend')}

==================================================
SYSTEM PRINCIPLES
==================================================
• Macro defines permission
• Market structure defines timing
• Sentiment accelerates — never overrides
• Shock logic activates separately

This is a decision-support system, not a trading bot.
"""

    return subject, body