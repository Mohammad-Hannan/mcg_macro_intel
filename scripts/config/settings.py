# config/settings.py

"""
MCG Intelligence — Central Settings
Phase 1 Production Config
"""

# =========================
# GENERAL
# =========================
SYSTEM_NAME = "MCG Intelligence"
DEFAULT_ACTION = "HOLD"
DATE_FORMAT = "%Y-%m-%d"

# =========================
# OUTPUT PATHS
# =========================
OUTPUT_DIR = "outputs"
LOG_DIR = "logs"

# =========================
# BTC STRUCTURE
# =========================
MA_SHORT_WINDOW = 50
MA_LONG_WINDOW = 200

# Volatility (annualized)
VOL_WINDOW_DAYS = 30
VOL_HIGH_THRESHOLD = 0.80  # 80% annualized

# =========================
# ETF FLOWS
# =========================
ETF_FLOW_WINDOW = 7
ETF_FLOW_POSITIVE = "positive"
ETF_FLOW_NEGATIVE = "negative"
ETF_FLOW_MIXED = "mixed"

# =========================
# FUNDING
# =========================
FUNDING_POS_THRESHOLD = 0.01
FUNDING_NEG_THRESHOLD = -0.01
FUNDING_NEUTRAL = "neutral"

# =========================
# PMI / MACRO
# =========================
PMI_TREND_DELTA = 0.2

REGIME_CONTRACTION = "CONTRACTION"
REGIME_EARLY_RECOVERY = "EARLY_RECOVERY"
REGIME_MID_EXPANSION = "MID_EXPANSION"
REGIME_LATE_CYCLE = "LATE_CYCLE"
REGIME_UNCLEAR = "REGIME_UNCLEAR"

# =========================
# FAIL-SAFE DEFAULTS
# =========================
DEFAULT_STRUCTURE = {
    "above_50dma": "no",
    "above_200dma": "no",
    "volatility": "high",
}

DEFAULT_FLOWS = {
    "etf_flow_regime": ETF_FLOW_MIXED
}

DEFAULT_FUNDING = {
    "funding_regime": FUNDING_NEUTRAL
}