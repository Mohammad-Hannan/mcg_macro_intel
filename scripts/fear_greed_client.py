import requests
from datetime import datetime

CMC_FNG_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"

# If using Alternative.me fallback
ALT_FNG_URL = "https://api.alternative.me/fng/"

def fetch_fear_greed():
    """
    Fetch Fear & Greed Index.
    Uses Alternative.me as free fallback.
    """

    try:
        r = requests.get(ALT_FNG_URL, timeout=10)
        data = r.json()

        value = int(data["data"][0]["value"])
        classification = data["data"][0]["value_classification"]
        timestamp = data["data"][0]["timestamp"]

        return {
            "value": value,
            "classification": classification.lower().replace(" ", "_"),
            "timestamp": timestamp,
            "source": "alternative_me"
        }

    except Exception as e:
        print("Fear & Greed fetch error:", e)
        return None


def classify_tactical_bias(fg_value):
    """
    Map Fear & Greed value to tactical bias.
    """

    if fg_value <= 20:
        return "TACTICAL_ADD_STRONG"
    elif fg_value <= 40:
        return "TACTICAL_ADD"
    elif fg_value <= 60:
        return "TACTICAL_HOLD"
    elif fg_value <= 75:
        return "TACTICAL_TRIM_PREP"
    else:
        return "TACTICAL_TRIM"