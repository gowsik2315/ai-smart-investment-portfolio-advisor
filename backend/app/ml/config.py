"""
Volatility Forecasting — Configuration

Single source of truth for the universe, the forecast horizon and the
on-disk locations. Training and inference both import from here so the
two cannot disagree about what is being predicted.
"""

from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────
# backend/app/ml/config.py -> backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# Parquet cache of downloaded price history
CACHE_DIR = BACKEND_DIR / "data_cache"

# Trained model artifacts. Note that .gitignore excludes *.joblib, so
# artifacts stay local and are not committed.
MODELS_DIR = BACKEND_DIR / "models"

# Default artifact the API loads at startup
DEFAULT_MODEL_PATH = MODELS_DIR / "volatility_model.joblib"


# ── Universe ─────────────────────────────────────────────────────────
# Liquid NSE large caps across distinct sectors, so the training set is
# not nine correlated banks.
TRAINING_TICKERS = [
    "RELIANCE.NS",    # Energy / conglomerate
    "TCS.NS",         # IT services
    "HDFCBANK.NS",    # Banking
    "INFY.NS",        # IT services
    "ICICIBANK.NS",   # Banking
    "HINDUNILVR.NS",  # FMCG
    "ITC.NS",         # FMCG / tobacco
    "LT.NS",          # Infrastructure
    "MARUTI.NS",      # Automotive
    "SUNPHARMA.NS",   # Pharmaceuticals
]

# Market index. Used as a feature (index volatility is a strong
# predictor of single-name volatility) and never as a training target.
INDEX_TICKER = "^NSEI"  # Nifty 50

# History depth for training
HISTORY_PERIOD = "10y"


# ── Target definition ────────────────────────────────────────────────
# Predict realised volatility over the NEXT 21 trading days (~1 month),
# annualised by sqrt(252).
HORIZON_DAYS = 21
TRADING_DAYS_PER_YEAR = 252

TARGET_COLUMN = f"target_rv_{HORIZON_DAYS}d"

# Because consecutive 21-day targets overlap, a random train/test split
# leaks the future into training. Splits must be chronological AND leave
# at least this many days of gap between train and test.
EMBARGO_DAYS = HORIZON_DAYS


# ── Inference ────────────────────────────────────────────────────────
# Trailing window used to compute features at prediction time. Must
# comfortably exceed the longest lookback in features.py (252 for the
# 52-week drawdown) plus slack for non-trading days.
INFERENCE_LOOKBACK_DAYS = 420

# Sanity bounds on any volatility the service will hand downstream.
# A forecast outside this range indicates a broken model or bad data
# rather than a real market condition, and is rejected.
MIN_PLAUSIBLE_VOLATILITY = 0.01   # 1% annualised
MAX_PLAUSIBLE_VOLATILITY = 3.00   # 300% annualised

# Cache lifetime for downloaded history, in hours. Daily bars do not
# change intraday, so a day is plenty.
CACHE_TTL_HOURS = 24


# ── Trend outlook ────────────────────────────────────────────────────
# The stock-trend outlook shares the volatility module's feature pipeline
# and its HORIZON_DAYS, so the probability of a rise and the expected
# price range always describe the same 21-day window.
DEFAULT_TREND_MODEL_PATH = MODELS_DIR / "trend_model.joblib"

# Fewest daily bars an outlook will be produced from (~6 months). Below
# this the 63-day momentum and the base rate are too thin to mean anything.
TREND_MIN_HISTORY_ROWS = 126

# How many completed 21-day windows the historical base rate averages
# over (~3 years). Windows overlap, so this is not an independent sample.
TREND_BASE_RATE_WINDOWS = 756
