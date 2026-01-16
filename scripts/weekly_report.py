import json
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
REPORT_DIR = BASE_DIR / "reports" / "weekly"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------
# STEP 9.1 — Load Daily Outputs
# -------------------------------

def load_recent_daily_files(days=7):
    """
    Load the most recent daily JSON files.
    """
    files = sorted(OUTPUT_DIR.glob("mcg_daily_*.json"))
    return files[-days:]


def load_daily_data(files):
    """
    Read daily JSON files safely.
    """
    data = []
    for f in files:
        try:
            with open(f, "r") as fh:
                data.append(json.load(fh))
        except Exception as e:
            print(f"Skipping {f.name}: {e}")
    return data


def build_weekly_context(daily_data):
    """
    Use latest available day as weekly snapshot.
    """
    if not daily_data:
        raise ValueError("No daily data available for weekly report")

    latest = daily_data[-1]

    return {
        "week_ending": latest["date"],
        "macro_regime": latest["macro_regime"],
        "btc_structure": latest["btc_structure"],
        "institutional_flows": latest["institutional_flows"],
        "funding": latest["funding"],
        "final_action": latest["final_action"],
        "days_included": len(daily_data),
    }


def save_weekly_context(context):
    """
    Save weekly context as JSON.
    """
    date_str = context["week_ending"]
    out_file = REPORT_DIR / f"mcg_weekly_context_{date_str}.json"

    with open(out_file, "w") as f:
        json.dump(context, f, indent=2)

    return out_file


# -------------------------------
# STEP 9.2 — Generate Report
# -------------------------------

def generate_weekly_report(context):
    """
    Convert weekly context into plain-English Markdown report.
    """
    date = context["week_ending"]
    macro = context["macro_regime"]
    structure = context["btc_structure"]
    flows = context["institutional_flows"]
    funding = context["funding"]
    action = context["final_action"]

    lines = []

    lines.append("# MCG Weekly Bitcoin Intelligence")
    lines.append(f"**Week Ending:** {date}")
    lines.append("")

    lines.append("## Macro Environment")
    lines.append(
        f"The macro regime is currently **{macro.replace('_', ' ').title()}**. "
        "This regime determines how much risk the system is allowed to take."
    )
    lines.append("")

    lines.append("## Market Structure")
    lines.append(f"- Above 50-day moving average: **{structure['above_50dma'].upper()}**")
    lines.append(f"- Above 200-day moving average: **{structure['above_200dma'].upper()}**")
    lines.append(f"- Volatility regime: **{structure['volatility'].upper()}**")
    lines.append("")

    lines.append("## Institutional Activity")
    lines.append(f"- ETF flow regime: **{flows['etf_flow_regime'].upper()}**")
    lines.append(f"- Funding rate regime: **{funding['funding_regime'].upper()}**")
    lines.append("")

    lines.append("## System Decision")
    lines.append(f"**Recommended Action:** **{action}**")
    lines.append("")

    if action == "ADD":
        lines.append(
            "Conditions are constructive. The system allows adding exposure within predefined risk limits."
        )
    elif action == "TRIM":
        lines.append(
            "Risk conditions are elevated. The system recommends reducing exposure."
        )
    else:
        lines.append(
            "Signals are mixed or unclear. The system recommends holding current exposure and waiting for confirmation."
        )

    lines.append("")
    lines.append(
        "_MCG Intelligence is a rules-based system. Macro conditions always take priority over short-term signals._"
    )

    return "\n".join(lines)


def save_weekly_report(report_text, date):
    """
    Save weekly report Markdown file.
    """
    out_file = REPORT_DIR / f"mcg_weekly_report_{date}.md"
    with open(out_file, "w") as f:
        f.write(report_text)
    return out_file


# -------------------------------
# Runner
# -------------------------------

def run_weekly_report():
    daily_files = load_recent_daily_files()
    daily_data = load_daily_data(daily_files)

    context = build_weekly_context(daily_data)
    context_file = save_weekly_context(context)

    report_text = generate_weekly_report(context)
    report_file = save_weekly_report(report_text, context["week_ending"])

    print("Weekly report generated successfully.")
    print(f"Context file: {context_file}")
    print(f"Report file: {report_file}")


if __name__ == "__main__":
    run_weekly_report()