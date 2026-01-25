import os
import json
import requests

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO").split(",")

LATEST_JSON = "public/daily/latest.json"

def load_signal():
    with open(LATEST_JSON, "r") as f:
        return json.load(f)

def build_email(data):
    subject = f"MCG Daily Signal — {data['final_action']} ({data['date']})"

    body = f"""
MCG Intelligence — Daily Signal

Date: {data['date']}
Macro Regime: {data['macro_regime']}

BTC Structure
- Above 50 DMA: {data['btc_structure']['above_50dma']}
- Above 200 DMA: {data['btc_structure']['above_200dma']}
- Volatility: {data['btc_structure']['volatility']}

Institutional Flows
- ETF Flow Regime: {data['institutional_flows']['etf_flow_regime']}

Funding
- Funding Regime: {data['funding']['funding_regime']}

PMI
- 3M Avg: {data['pmi'].get('pmi_3m_avg')}
- Trend: {data['pmi'].get('pmi_trend')}

FINAL ACTION: {data['final_action']}
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
    print("Email sent successfully")