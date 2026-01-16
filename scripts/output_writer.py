import json
import os
from datetime import datetime
from config.settings import OUTPUT_DIR, DATE_FORMAT


def write_daily_output(data: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    date_str = data["date"]
    filename = f"mcg_daily_{date_str}.json"
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path