import json
from pathlib import Path

OUTPUT_DIR = Path("outputs")
PUBLIC_DIR = Path("public/daily")

OUTPUT_DIR.mkdir(exist_ok=True)
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

def write_daily_output(data):
    date = data["date"]

    # Internal archive
    internal_path = OUTPUT_DIR / f"mcg_daily_{date}.json"

    # Public endpoint
    public_path = PUBLIC_DIR / "latest.json"

    with open(internal_path, "w") as f:
        json.dump(data, f, indent=2)

    with open(public_path, "w") as f:
        json.dump(data, f, indent=2)

    return {
        "internal": str(internal_path),
        "public": str(public_path)
    }