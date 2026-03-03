import requests


BINANCE_FUTURES_BASE = "https://fapi.binance.com"
BINANCE_SPOT_BASE = "https://api.binance.com"


def fetch_funding_rate():
    url = f"{BINANCE_FUTURES_BASE}/fapi/v1/premiumIndex?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return float(data["lastFundingRate"])


def fetch_open_interest():
    url = f"{BINANCE_FUTURES_BASE}/fapi/v1/openInterest?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return float(data["openInterest"])


def fetch_futures_price():
    url = f"{BINANCE_FUTURES_BASE}/fapi/v1/ticker/price?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return float(data["price"])


def fetch_spot_price():
    url = f"{BINANCE_SPOT_BASE}/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return float(data["price"])


def compute_basis(futures_price, spot_price):
    return (futures_price - spot_price) / spot_price * 100