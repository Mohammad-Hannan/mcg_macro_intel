import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "outputs"
PUBLIC_DIR = BASE_DIR / "public" / "daily"

OUTPUT_DIR.mkdir(exist_ok=True)
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

def write_daily_output(data: dict) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Force correct date every run
    data["date"] = today

    dated_path = OUTPUT_DIR / f"mcg_daily_{today}.json"
    latest_path = PUBLIC_DIR / "latest.json"

    with open(dated_path, "w") as f:
        json.dump(data, f, indent=2)

    with open(latest_path, "w") as f:
        json.dump(data, f, indent=2)

    return str(latest_path)