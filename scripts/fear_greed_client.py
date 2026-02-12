import requests
from datetime import datetime

FNG_URL = "https://api.alternative.me/fng/?limit=1&format=json"


def fetch_fear_greed():
    try:
        r = requests.get(FNG_URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        if "data" not in data or len(data["data"]) == 0:
            return None

        entry = data["data"][0]

        value = int(entry["value"])
        classification = entry["value_classification"].lower().replace(" ", "_")
        timestamp = entry["timestamp"]

        return {
            "value": value,
            "classification": classification,
            "timestamp": timestamp,
            "source": "alternative_me"
        }

    except Exception as e:
        print("Fear & Greed fetch error:", e)
        return None


def classify_tactical_bias(value):
    if value <= 20:
        return "TACTICAL_ADD_STRONG"
    elif value <= 40:
        return "TACTICAL_ADD"
    elif value <= 60:
        return "TACTICAL_HOLD"
    elif value <= 75:
        return "TACTICAL_TRIM_PREP"
    else:
        return "TACTICAL_TRIM"