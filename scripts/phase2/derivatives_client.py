import requests


DERIBIT_URL = "https://www.deribit.com/api/v2"


# ---------------------------------------------------
# Fetch BTC Perpetual Instrument Data
# ---------------------------------------------------

def fetch_perp_data():
    """
    Pull BTC-PERPETUAL market data from Deribit.
    This contains:
    - mark_price
    - funding_rate
    - open_interest
    """

    url = f"{DERIBIT_URL}/public/ticker"
    params = {"instrument_name": "BTC-PERPETUAL"}

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()["result"]

    return data


# ---------------------------------------------------
# Funding Rate
# ---------------------------------------------------

def fetch_funding_rate():
    data = fetch_perp_data()
    return float(data["funding_8h"])


# ---------------------------------------------------
# Open Interest
# ---------------------------------------------------

def fetch_open_interest():
    data = fetch_perp_data()
    return float(data["open_interest"])


# ---------------------------------------------------
# Futures Price (Perpetual mark price)
# ---------------------------------------------------

def fetch_futures_price():
    data = fetch_perp_data()
    return float(data["mark_price"])


# ---------------------------------------------------
# Spot Price
# ---------------------------------------------------

def fetch_spot_price():
    """
    Uses Deribit BTC index price
    """

    url = f"{DERIBIT_URL}/public/get_index_price"
    params = {"index_name": "btc_usd"}

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()["result"]

    return float(data["index_price"])


# ---------------------------------------------------
# Basis Calculation
# ---------------------------------------------------

def compute_basis(futures_price, spot_price):

    if spot_price == 0:
        return 0

    return (futures_price - spot_price) / spot_price