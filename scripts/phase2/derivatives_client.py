import requests


BASE_URL = "https://www.deribit.com/api/v2"


# ---------------------------------------------------
# Funding Rate
# ---------------------------------------------------

def fetch_funding_rate():
    """
    Fetch BTC perpetual funding rate from Deribit ticker
    """

    url = f"{BASE_URL}/public/ticker"

    params = {
        "instrument_name": "BTC-PERPETUAL"
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()

    return float(data["result"]["funding_8h"])


# ---------------------------------------------------
# Open Interest
# ---------------------------------------------------

def fetch_open_interest():

    url = f"{BASE_URL}/public/get_book_summary_by_instrument"

    params = {
        "instrument_name": "BTC-PERPETUAL"
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()

    return float(data["result"][0]["open_interest"])


# ---------------------------------------------------
# Futures Price
# ---------------------------------------------------

def fetch_futures_price():

    url = f"{BASE_URL}/public/ticker"

    params = {
        "instrument_name": "BTC-PERPETUAL"
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()

    return float(data["result"]["last_price"])


# ---------------------------------------------------
# Spot Price
# ---------------------------------------------------

def fetch_spot_price():

    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()

    return float(data["bitcoin"]["usd"])


# ---------------------------------------------------
# Basis Calculation
# ---------------------------------------------------

def compute_basis(futures_price, spot_price):

    if spot_price == 0:
        return 0

    return (futures_price - spot_price) / spot_price