import json
from pathlib import Path
from datetime import datetime


# Base directories
ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT / "outputs"
PUBLIC_DAILY_DIR = ROOT / "public" / "daily"

OUTPUTS_DIR.mkdir(exist_ok=True)
PUBLIC_DAILY_DIR.mkdir(parents=True, exist_ok=True)


def write_daily_output(data: dict) -> Path:
    """
    Writes:
    1) Dated output to outputs/
    2) Latest snapshot to public/daily/latest.json (for GitHub Pages)
    """

    date_str = data.get("date") or datetime.utcnow().strftime("%Y-%m-%d")

    # 1️⃣ Write dated output (internal)
    dated_path = OUTPUTS_DIR / f"mcg_daily_{date_str}.json"
    with open(dated_path, "w") as f:
        json.dump(data, f, indent=2)

    # 2️⃣ Write public latest.json (LIVE OUTPUT)
    latest_path = PUBLIC_DAILY_DIR / "latest.json"
    with open(latest_path, "w") as f:
        json.dump(data, f, indent=2)

    return latest_path