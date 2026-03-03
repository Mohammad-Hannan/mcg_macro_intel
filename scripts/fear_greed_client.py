import requests
import json
import os
import time
from datetime import datetime, timedelta

FNG_URL = "https://api.alternative.me/fng/?limit=1&format=json"
CACHE_PATH = "scripts/phase2/fng_cache.json"
MAX_RETRIES = 3
TIMEOUT = 5
CACHE_EXPIRY_DAYS = 3


def _save_cache(data):
    try:
        with open(CACHE_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def _load_cache():
    if not os.path.exists(CACHE_PATH):
        return None

    try:
        with open(CACHE_PATH, "r") as f:
            data = json.load(f)

        ts = datetime.utcfromtimestamp(int(data["timestamp"]))
        if datetime.utcnow() - ts > timedelta(days=CACHE_EXPIRY_DAYS):
            return None

        return data

    except Exception:
        return None


def fetch_fear_greed():

    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(FNG_URL, timeout=TIMEOUT)
            r.raise_for_status()
            payload = r.json()

            raw = payload["data"][0]

            data = {
                "value": int(raw["value"]),
                "classification": raw["value_classification"].lower().replace(" ", "_"),
                "timestamp": raw["timestamp"],
                "source": "alternative_me"
            }

            _save_cache(data)
            return data

        except Exception:
            time.sleep(1)

    # ---- If API fails → fallback to cache ----
    cached = _load_cache()
    if cached:
        return cached

    return None


def classify_tactical_bias(value):

    if value is None:
        return "TACTICAL_HOLD"

    if value <= 15:
        return "TACTICAL_ADD_STRONG"
    elif value <= 30:
        return "TACTICAL_ADD"
    elif value >= 85:
        return "TACTICAL_TRIM_STRONG"
    elif value >= 70:
        return "TACTICAL_TRIM"

    return "TACTICAL_HOLD"