import os
import json
import requests
from datetime import datetime

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO").split(",")

LATEST_JSON = "public/daily/latest.json"


def load_signal():
    with open(LATEST_JSON, "r") as f:
        return json.load(f)


def build_email(data):
    # ---- Extract fields safely ----
    date = data.get("date")
    macro = data.get("macro_regime")
    final_action = data.get("final_action")
    shock_mode = data.get("shock_mode", False)
    weekend_mode = data.get("weekend_mode", False)

    btc = data.get("btc_structure", {})
    flows = data.get("institutional_flows", {})
    funding = data.get("funding", {})
    pmi = data.get("pmi", {})
    fg = data.get("fear_greed", {})
    tactical = data.get("tactical_bias", "TACTICAL_HOLD")

    # ---- Formatting helpers ----
    shock_text = "🚨 SHOCK MODE ACTIVE" if shock_mode else "Normal"
    weekend_text = "Yes" if weekend_mode else "No"

    fg_value = fg.get("value", "N/A")
    fg_class = fg.get("classification", "N/A")

    # ---- Subject ----
    subject = f"MCG Intelligence — {final_action} | {date}"

    # ---- Body ----
    body = f"""
MCG INTELLIGENCE SYSTEM — DAILY UPDATE
Date: {date}

==================================================
CORE DECISION
==================================================
Final Action: {final_action}
Macro Regime: {macro}
Shock Mode: {shock_text}
Weekend Mode: {weekend_text}

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


def send_email(subject, body):
    url = "https://api.sendgrid.com/v3/mail/send"

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "personalizations": [{
            "to": [{"email": e.strip()} for e in EMAIL_TO],
            "subject": subject
        }],
        "from": {"email": EMAIL_FROM},
        "content": [{
            "type": "text/plain",
            "value": body
        }]
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()


if __name__ == "__main__":
    data = load_signal()
    subject, body = build_email(data)
    send_email(subject, body)
    print("Email sent successfully.")