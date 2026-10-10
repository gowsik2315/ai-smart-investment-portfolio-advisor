"""
Volatility Forecasting — Feature Engineering

THIS MODULE IS SHARED BY TRAINING AND INFERENCE. Import
`build_features` in your training script too. If training builds its
features anywhere else, the served model receives inputs it never saw
during fitting, and the failure is silent: predictions come back
plausible-looking and wrong.

Leakage contract
----------------
Every feature on row `t` uses information available at the close of day
`t` and no later. The target on row `t` is realised volatility over days
`t+1 .. t+HORIZON_DAYS`, so it is strictly in the future.

Because consecutive targets share overlapping return windows, rows are
NOT independent. A random train/test split leaks; see
`chronological_split`, which also applies the required embargo.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from app.ml.config import (
    EMBARGO_DAYS,
    HORIZON_DAYS,
    TARGET_COLUMN,
    TARGET_UP_COLUMN,
    TRADING_DAYS_PER_YEAR,
)

ANNUALISE = np.sqrt(TRADING_DAYS_PER_YEAR)

# Longest lookback used below. Rows before this have incomplete features.
MAX_LOOKBACK = 252

# Canonical feature order. The trained artifact records this list, and
# the prediction service refuses to run if the live build disagrees.
FEATURE_NAMES: List[str] = [
    # Recent returns
    "ret_1d",
    "ret_lag_1",
    "ret_lag_2",
    "ret_lag_3",
    "ret_lag_4",
    "ret_lag_5",
    # Realised volatility at several horizons (the HAR-style core)
    "rv_5",
    "rv_10",
    "rv_21",
    "rv_63",
    # Volatility term structure: is short-horizon vol above or below long?
    "rv_ratio_5_21",
    "rv_ratio_21_63",
    # Range-based estimators — use intraday high/low, so they carry
    # information daily closes alone do not
    "parkinson_21",
    "garman_klass_21",
    # Activity
    "volume_ratio_20",
    # Trend / stress
    "mom_21",
    "mom_63",
    "rsi_14",
    "drawdown_52w",
    # Market context
    "idx_rv_21",
    "idx_mom_21",
]


def _log_returns(close: pd.Series) -> pd.Series:
    """Daily log returns. Index preserved; first row is NaN."""
    return np.log(close / close.shift(1))


def _realised_vol(log_ret: pd.Series, window: int) -> pd.Series:
    """
    Annualised realised volatility over a trailing window ending at t.

    Uses the sample standard deviation of log returns.
    """
    return log_ret.rolling(window, min_periods=window).std() * ANNUALISE


def _parkinson(high: pd.Series, low: pd.Series, window: int) -> pd.Series:
    """
    Parkinson range volatility estimator.

        sigma = sqrt( mean( ln(H/L)^2 ) / (4 ln 2) ) * sqrt(252)

    More efficient than close-to-close for a given sample size, because
    the daily range says more about dispersion than one closing price.
    """
    hl = np.log(high / low) ** 2
    mean_hl = hl.rolling(window, min_periods=window).mean()
    return np.sqrt(mean_hl / (4.0 * np.log(2.0))) * ANNUALISE


def _garman_klass(
    open_: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int,
) -> pd.Series:
    """
    Garman-Klass volatility estimator.

        term = 0.5 * ln(H/L)^2 - (2 ln2 - 1) * ln(C/O)^2

    The per-day term can come out negative, which is an artefact of the
    estimator rather than meaningful, so the windowed mean is floored at
    zero before the square root.
    """
    term = (
        0.5 * np.log(high / low) ** 2
        - (2.0 * np.log(2.0) - 1.0) * np.log(close / open_) ** 2
    )
    mean_term = term.rolling(window, min_periods=window).mean()
    return np.sqrt(mean_term.clip(lower=0.0)) * ANNUALISE


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index over a simple moving average of gains/losses.

    Returned on its native 0-100 scale.
    """
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    avg_gain = gain.rolling(window, min_periods=window).mean()
    avg_loss = loss.rolling(window, min_periods=window).mean()

    # No losses in the window -> RSI 100 by definition; guard the divide.
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.where(avg_loss != 0.0, 100.0)


def build_features(
    ohlcv: pd.DataFrame,
    index_ohlcv: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Build the feature matrix for one instrument.

    Args:
        ohlcv: daily OHLCV for the instrument, indexed by date, as
            returned by `app.ml.data.load_history`
        index_ohlcv: daily OHLCV for the market index. If omitted, the
            two `idx_*` features are filled with NaN and any row needing
            them is dropped by `build_training_table`.

    Returns:
        DataFrame indexed by date with exactly `FEATURE_NAMES` as
        columns, in that order. Early rows contain NaN where a lookback
        window is not yet full; NaNs are left in place so the caller can
        decide how to handle them.
    """
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(ohlcv.columns)
    if missing:
        raise ValueError(f"build_features: ohlcv missing columns {sorted(missing)}")

    df = ohlcv.sort_index()
    close, high, low, open_, volume = (
        df["close"], df["high"], df["low"], df["open"], df["volume"]
    )

    log_ret = _log_returns(close)
    out = pd.DataFrame(index=df.index)

    # ── Recent returns ──────────────────────────────────────────────
    out["ret_1d"] = log_ret
    for lag in range(1, 6):
        out[f"ret_lag_{lag}"] = log_ret.shift(lag)

    # ── Realised volatility ─────────────────────────────────────────
    rv_5 = _realised_vol(log_ret, 5)
    rv_10 = _realised_vol(log_ret, 10)
    rv_21 = _realised_vol(log_ret, 21)
    rv_63 = _realised_vol(log_ret, 63)

    out["rv_5"] = rv_5
    out["rv_10"] = rv_10
    out["rv_21"] = rv_21
    out["rv_63"] = rv_63

    # Ratios rather than differences, so the term structure is on a
    # comparable scale across calm and stressed regimes.
    out["rv_ratio_5_21"] = rv_5 / rv_21.replace(0.0, np.nan)
    out["rv_ratio_21_63"] = rv_21 / rv_63.replace(0.0, np.nan)

    # ── Range-based estimators ──────────────────────────────────────
    out["parkinson_21"] = _parkinson(high, low, 21)
    out["garman_klass_21"] = _garman_klass(open_, high, low, close, 21)

    # ── Activity ────────────────────────────────────────────────────
    vol_mean_20 = volume.rolling(20, min_periods=20).mean()
    out["volume_ratio_20"] = volume / vol_mean_20.replace(0.0, np.nan)

    # ── Trend / stress ──────────────────────────────────────────────
    out["mom_21"] = np.log(close / close.shift(21))
    out["mom_63"] = np.log(close / close.shift(63))
    out["rsi_14"] = _rsi(close, 14)

    # Distance below the trailing 52-week high; <= 0 by construction.
    high_52w = close.rolling(MAX_LOOKBACK, min_periods=MAX_LOOKBACK).max()
    out["drawdown_52w"] = (close / high_52w) - 1.0

    # ── Market context ──────────────────────────────────────────────
    if index_ohlcv is not None and not index_ohlcv.empty:
        idx_close = index_ohlcv.sort_index()["close"]
        idx_log_ret = _log_returns(idx_close)

        idx_rv_21 = _realised_vol(idx_log_ret, 21)
        idx_mom_21 = np.log(idx_close / idx_close.shift(21))

        # Align the index onto the instrument's calendar. ffill only
        # carries values forward from earlier dates, so no future index
        # observation can reach an earlier row.
        out["idx_rv_21"] = idx_rv_21.reindex(out.index).ffill()
        out["idx_mom_21"] = idx_mom_21.reindex(out.index).ffill()
    else:
        out["idx_rv_21"] = np.nan
        out["idx_mom_21"] = np.nan

    # Infinities arise from zero-denominator edge cases; treat as missing.
    out = out.replace([np.inf, -np.inf], np.nan)

    return out[FEATURE_NAMES]


def build_target(
    ohlcv: pd.DataFrame,
    horizon: int = HORIZON_DAYS,
) -> pd.Series:
    """
    Realised volatility over the NEXT `horizon` trading days, annualised.

    The value on row `t` is the standard deviation of log returns on days
    `t+1 .. t+horizon`. Implemented as a trailing rolling std shifted
    back by `horizon`, which is why the last `horizon` rows are NaN —
    their future has not happened yet.
    """
    log_ret = _log_returns(ohlcv.sort_index()["close"])
    trailing = log_ret.rolling(horizon, min_periods=horizon).std()
    forward = trailing.shift(-horizon) * ANNUALISE
    return forward.rename(TARGET_COLUMN)


def _forward_log_return(ohlcv: pd.DataFrame, horizon: int = HORIZON_DAYS) -> pd.Series:
    """
    Log return from the close on row `t` to the close on row `t + horizon`.

    The single definition of the forward return: `build_target_up` and
    `app.ml.trend` both derive from it, so they cannot disagree. It looks
    ahead by `shift(-horizon)`, exactly as `build_target` does, so the last
    `horizon` rows are NaN because that future has not happened yet.
    """
    close = ohlcv.sort_index()["close"]
    return np.log(close.shift(-horizon) / close)


def build_target_up(
    ohlcv: pd.DataFrame,
    horizon: int = HORIZON_DAYS,
) -> pd.Series:
    """
    Direction label: 1 if the close `horizon` trading days ahead is above
    today's close, else 0. NaN where that future close is not yet known.

    Aligned row-for-row with `build_target`. Both use the same `horizon`
    and the same `shift(-horizon)`, and both need the closes on rows
    `t .. t + horizon`, so each is NaN on exactly the same final `horizon`
    rows and defined on exactly the same rows elsewhere. Joining them never
    costs a row.

    "Above" is strict: a forward return of exactly zero is labelled 0.
    This is a LABEL, not a feature, and is deliberately not in
    `FEATURE_NAMES`.
    """
    forward = _forward_log_return(ohlcv, horizon)
    label = (forward > 0).astype(float).where(forward.notna())
    return label.rename(TARGET_UP_COLUMN)


def build_training_table(
    ohlcv: pd.DataFrame,
    index_ohlcv: Optional[pd.DataFrame] = None,
    horizon: int = HORIZON_DAYS,
    ticker: Optional[str] = None,
) -> pd.DataFrame:
    """
    Feature matrix joined to both targets, with incomplete rows dropped.

    Args:
        ticker: when given, added as a `ticker` column so several
            instruments can be concatenated into one panel.

    Returns:
        DataFrame with `FEATURE_NAMES` + TARGET_COLUMN + TARGET_UP_COLUMN
        (+ `ticker`), indexed by date, containing only fully-populated rows.

    The two targets are LABELS. Select model inputs with
    `table[FEATURE_NAMES]`, never by dropping one label and keeping the
    rest: the other label is a future quantity, and a model fitted on it
    scores beautifully offline and is worthless live. For a trend
    classifier that must not even see the volatility label, use
    `app.ml.trend.build_trend_training_table`.
    """
    features = build_features(ohlcv, index_ohlcv)
    target = build_target(ohlcv, horizon)
    target_up = build_target_up(ohlcv, horizon)

    table = features.join(target, how="inner").join(target_up, how="inner")
    table = table.dropna()

    if ticker is not None:
        table["ticker"] = ticker

    return table


def latest_feature_row(
    ohlcv: pd.DataFrame,
    index_ohlcv: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.Timestamp]:
    """
    Most recent fully-populated feature row, for live prediction.

    Returns:
        (one-row DataFrame in FEATURE_NAMES order, the date of that row)

    Raises:
        ValueError: if no row has a complete feature set, which means the
            supplied history is shorter than the longest lookback.
    """
    features = build_features(ohlcv, index_ohlcv)
    complete = features.dropna()

    if complete.empty:
        raise ValueError(
            f"No complete feature row available: need at least "
            f"{MAX_LOOKBACK} trading days of history, got {len(features)} rows."
        )

    as_of = complete.index[-1]
    return complete.iloc[[-1]][FEATURE_NAMES], as_of


def chronological_split(
    table: pd.DataFrame,
    test_fraction: float = 0.2,
    embargo: int = EMBARGO_DAYS,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split a training table by time, with an embargo gap measured in
    TRADING DATES.

    The gap matters. Targets are 21-day forward windows, so the target on
    the last training row is built from returns that extend 21 days into
    the test period. Splitting without the gap lets the model see part of
    its own test window during fitting and inflates every metric.

    The embargo counts unique DATES, not rows. That distinction is
    essential for a multi-ticker panel: with 10 tickers there are 10 rows
    per date, so a 21-ROW embargo would leave only ~2 days of separation
    and the leak it exists to prevent would still be wide open.

    Args:
        table: output of `build_training_table`, indexed by date. May
            hold several tickers (10 rows per date for a 10-name panel).
        test_fraction: share of the trading DATES held out at the end
        embargo: number of trading dates discarded between train and test

    Returns:
        (train, test)
    """
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be between 0 and 1")

    ordered = table.sort_index()
    dates = ordered.index.unique().sort_values()
    n_dates = len(dates)
    n_test_dates = int(n_dates * test_fraction)

    if n_test_dates <= 0 or (n_dates - n_test_dates - embargo) <= 0:
        raise ValueError(
            f"Not enough rows ({len(ordered)} rows over {n_dates} dates) for a "
            f"{test_fraction:.0%} test split with a {embargo}-date embargo."
        )

    test_start_pos = n_dates - n_test_dates
    test_start = dates[test_start_pos]
    train_end = dates[test_start_pos - embargo - 1]

    train = ordered.loc[:train_end]
    test = ordered.loc[test_start:]

    return train, test
