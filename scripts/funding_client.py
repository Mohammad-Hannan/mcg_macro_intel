from scripts.phase2.derivatives_client import fetch_funding_rate


def fetch_funding_rates():
    """
    Fetch funding rate from Deribit via derivatives client
    """

    funding = fetch_funding_rate()

    return {
        "funding": funding
    }


def classify_funding(data):
    """
    Simple funding regime classification
    """

    funding = data.get("funding", 0)

    if funding > 0.01:
        return "overheated"

    if funding < -0.01:
        return "bearish"

    return "neutral"