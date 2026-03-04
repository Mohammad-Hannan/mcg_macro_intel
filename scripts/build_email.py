def build_email(data):

    date = data.get("date")
    macro = data.get("macro_regime")
    final_action = data.get("final_action")

    shock = data.get("shock", {})
    shock_mode = shock.get("shock_mode", False)

    subject = f"MCG Intelligence — {final_action} | {date}"

    body = f"""
MCG INTELLIGENCE SYSTEM — DAILY UPDATE
Date: {date}

Final Action: {final_action}
Macro Regime: {macro}
Shock Mode: {"ACTIVE" if shock_mode else "Normal"}

This is a decision-support system, not a trading bot.
"""

    return subject, body