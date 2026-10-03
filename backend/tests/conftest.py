"""
Shared test fixtures.

All price data here is synthetic. The tests must not touch the network:
yfinance is rate-limited and occasionally returns empty frames, which
would make the suite flaky for reasons unrelated to the code under test.
"""

import numpy as np
import pandas as pd
import pytest


def make_ohlcv(
    n_days: int = 900,
    seed: int = 7,
    annual_vol: float = 0.25,
    annual_drift: float = 0.10,
    start: str = "2020-01-01",
) -> pd.DataFrame:
    """
    Generate a plausible daily OHLCV frame via geometric Brownian motion.

    Highs and lows are placed around each day's open/close so the
    range-based estimators (Parkinson, Garman-Klass) get sane inputs.
    """
    rng = np.random.default_rng(seed)
    dt = 1.0 / 252
    step_sigma = annual_vol * np.sqrt(dt)
    step_drift = dt * np.log1p(annual_drift) - 0.5 * step_sigma ** 2

    log_steps = rng.normal(step_drift, step_sigma, n_days)
    close = 100.0 * np.exp(np.cumsum(log_steps))

    open_ = np.empty_like(close)
    open_[0] = 100.0
    open_[1:] = close[:-1]

    # Intraday extremes extend beyond the open/close band
    spread = np.abs(rng.normal(0, step_sigma, n_days)) * close
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread
    low = np.maximum(low, 0.01)  # never non-positive

    volume = rng.integers(1_000_000, 10_000_000, n_days)

    dates = pd.bdate_range(start=start, periods=n_days)

    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=pd.DatetimeIndex(dates, name="date"),
    )


@pytest.fixture
def ohlcv() -> pd.DataFrame:
    """Synthetic OHLCV for a single instrument."""
    return make_ohlcv()


@pytest.fixture
def index_ohlcv() -> pd.DataFrame:
    """Synthetic OHLCV standing in for the market index."""
    return make_ohlcv(seed=99, annual_vol=0.16, annual_drift=0.09)


@pytest.fixture
def short_ohlcv() -> pd.DataFrame:
    """Too little history for a complete feature row (252-day lookback)."""
    return make_ohlcv(n_days=60)
