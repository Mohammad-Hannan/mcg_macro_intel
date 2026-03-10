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

    # force new date every run
    data["date"] = today

    # add pipeline timestamp so file always changes
    data["pipeline_run"] = datetime.utcnow().isoformat()

    dated_path = OUTPUT_DIR / f"mcg_daily_{today}.json"
    latest_path = PUBLIC_DIR / "latest.json"

    with open(dated_path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    with open(latest_path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    return str(latest_path)