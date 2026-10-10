"""
Stock Trend Outlook — target, baselines, expected range and scoring.

What this predicts
------------------
The probability that a stock closes HIGHER, HORIZON_DAYS trading days from
now. It does not predict a price. Daily prices are close to a random walk,
and a single price target would claim precision that does not exist.

Why the baseline matters more than the model
--------------------------------------------
Over a 21-day window most large-cap stocks rise somewhat more often than
they fall, so a model that always says "up" is right well over half the
time. Accuracy on its own is therefore close to meaningless here. A model
only has value if it beats `base_rate_up`, the stock's own historical
frequency of rising, on a proper scoring rule (Brier / log-loss), not
merely on accuracy. `evaluate_trend_probabilities` reports both sides.

Features are shared with the volatility module (`app.ml.features`), so
training and inference cannot drift apart. Only the target differs.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.ml.config import (
    HORIZON_DAYS,
    TRADING_DAYS_PER_YEAR,
    TREND_BASE_RATE_WINDOWS,
)
from app.ml.features import _rsi, build_features

TREND_TARGET_COLUMN = f"target_up_{HORIZON_DAYS}d"
TREND_RETURN_COLUMN = f"fwd_ret_{HORIZON_DAYS}d"

# Two-sided normal quantiles for the 68% and 95% bands
Z_68 = 1.0
Z_95 = 1.959964


# ── Target ───────────────────────────────────────────────────────────

def build_trend_target(ohlcv: pd.DataFrame, horizon: int = HORIZON_DAYS) -> pd.DataFrame:
    """
    Forward log return and the up/down label, per row.

    Row `t` holds the move from the close on day `t` to the close on day
    `t + horizon`, so it is strictly in the future. The last `horizon`
    rows are NaN because their future has not happened yet.

    Returns:
        DataFrame with `TREND_RETURN_COLUMN` and `TREND_TARGET_COLUMN`
        (1.0 when the return is strictly positive, else 0.0).
    """
    close = ohlcv.sort_index()["close"]
    forward = np.log(close.shift(-horizon) / close)
    label = (forward > 0).astype(float).where(forward.notna())
    return pd.DataFrame({TREND_RETURN_COLUMN: forward, TREND_TARGET_COLUMN: label})


def build_trend_training_table(
    ohlcv: pd.DataFrame,
    index_ohlcv: Optional[pd.DataFrame] = None,
    horizon: int = HORIZON_DAYS,
    ticker: Optional[str] = None,
) -> pd.DataFrame:
    """
    `FEATURE_NAMES` + `TREND_TARGET_COLUMN` (+ `ticker`), complete rows only.

    The forward return is deliberately NOT included. It is the quantity the
    label is derived from, so a training script that selected "every column
    except the target" would otherwise feed the model its own answer.

    Split with `app.ml.features.chronological_split`; consecutive 21-day
    labels overlap, so a random split leaks.
    """
    features = build_features(ohlcv, index_ohlcv)
    target = build_trend_target(ohlcv, horizon)[[TREND_TARGET_COLUMN]]

    table = features.join(target, how="inner").dropna()
    if ticker is not None:
        table["ticker"] = ticker
    return table


# ── Descriptive trend (no prediction) ────────────────────────────────

def technical_trend_signal(ohlcv: pd.DataFrame) -> Dict[str, Any]:
    """
    Where the stock is trending NOW, from four simple technical signals.

    This is a description of the past, not a forecast, and the response
    labels it that way. Signals needing more history than is available are
    omitted rather than guessed.

    Returns:
        {"label": Bullish | Neutral | Bearish, "score": -1..1,
         "signals": [...], "rsi_14": float, "rsi_state": str}
    """
    close = ohlcv.sort_index()["close"].dropna()
    price = float(close.iloc[-1])
    signals: List[Dict[str, Any]] = []

    def add(name: str, label: str, value: float, bullish: bool, detail: str) -> None:
        signals.append({
            "name": name,
            "label": label,
            "value": round(float(value), 4),
            "bullish": bool(bullish),
            "detail": detail,
        })

    if len(close) >= 50:
        sma50 = float(close.tail(50).mean())
        above = price > sma50
        add("price_vs_sma50", "Price vs 50-day average", price / sma50 - 1.0, above,
            f"Price is {'above' if above else 'below'} its 50-day average")

    if len(close) >= 200:
        sma50 = float(close.tail(50).mean())
        sma200 = float(close.tail(200).mean())
        above = sma50 > sma200
        add("sma50_vs_sma200", "50-day vs 200-day average", sma50 / sma200 - 1.0, above,
            f"50-day average is {'above' if above else 'below'} the 200-day")

    if len(close) >= 22:
        mom = float(np.log(price / close.iloc[-22]))
        add("momentum_21d", "1-month momentum", mom, mom > 0,
            f"Price is {'up' if mom > 0 else 'down'} over the last 21 trading days")

    if len(close) >= 64:
        mom = float(np.log(price / close.iloc[-64]))
        add("momentum_63d", "3-month momentum", mom, mom > 0,
            f"Price is {'up' if mom > 0 else 'down'} over the last 63 trading days")

    bullish = sum(1 for s in signals if s["bullish"])
    score = (2 * bullish - len(signals)) / len(signals) if signals else 0.0

    if score >= 0.5:
        label = "Bullish"
    elif score <= -0.5:
        label = "Bearish"
    else:
        label = "Neutral"

    rsi_series = _rsi(close, 14).dropna()
    rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else None
    rsi_state = None
    if rsi is not None:
        rsi_state = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"

    return {
        "label": label,
        "score": round(score, 3),
        "signals": signals,
        "rsi_14": round(rsi, 1) if rsi is not None else None,
        "rsi_state": rsi_state,
    }


# ── Baseline ─────────────────────────────────────────────────────────

def base_rate_up(
    ohlcv: pd.DataFrame,
    horizon: int = HORIZON_DAYS,
    max_windows: int = TREND_BASE_RATE_WINDOWS,
) -> Optional[float]:
    """
    Share of this stock's recent completed windows that ended higher.

    This is the number a trained model has to beat. Windows overlap, so
    treat it as a rough frequency rather than a precisely measured one.

    Returns:
        A value in [0, 1], or None when there are too few windows.
    """
    forward = build_trend_target(ohlcv, horizon)[TREND_RETURN_COLUMN].dropna().tail(max_windows)
    if len(forward) < 63:
        return None
    return float((forward > 0).mean())


# ── Expected range ───────────────────────────────────────────────────

def expected_range(
    price: float,
    sigma: float,
    horizon: int = HORIZON_DAYS,
) -> List[Dict[str, float]]:
    """
    Price bands for each trading day out to `horizon`.

    Log-price is modelled as normal with standard deviation
    `sigma * sqrt(k / 252)` after k days, centred on today's price. The
    centre line carries NO directional view: it is today's price, so the
    range says how far the stock may move, not which way. Direction
    lives in the separate probability.

    Args:
        price: last close
        sigma: annualised volatility (decimal, e.g. 0.25)
        horizon: trading days to project

    Returns:
        One dict per day 0..horizon with `median` and the 68% / 95% bounds.
        Day 0 is the last close with zero width, so a chart cone starts
        from the final observed price.
    """
    if price <= 0 or not math.isfinite(price):
        raise ValueError(f"price must be positive and finite, got {price}")
    if sigma < 0 or not math.isfinite(sigma):
        raise ValueError(f"sigma must be non-negative and finite, got {sigma}")

    path = []
    for k in range(horizon + 1):
        spread = sigma * math.sqrt(k / TRADING_DAYS_PER_YEAR)
        path.append({
            "day": k,
            "median": round(price, 2),
            "lower_68": round(price * math.exp(-Z_68 * spread), 2),
            "upper_68": round(price * math.exp(Z_68 * spread), 2),
            "lower_95": round(price * math.exp(-Z_95 * spread), 2),
            "upper_95": round(price * math.exp(Z_95 * spread), 2),
        })
    return path


# ── Scoring ──────────────────────────────────────────────────────────

def evaluate_trend_probabilities(
    y_true,
    p_up,
    train_base_rate: float,
) -> Dict[str, Optional[float]]:
    """
    Score predicted probabilities against the baseline that matters.

    Pass the TRAIN-set share of rising windows as `train_base_rate`. The
    baseline must be built from information available before the test
    period; using the test set's own rate would flatter it.

    Returns metrics for the model and for the constant base-rate
    predictor, plus the Brier skill score (positive means the model beats
    the baseline; zero or negative means it does not).
    """
    y = np.asarray(y_true, dtype=float)
    p = np.clip(np.asarray(p_up, dtype=float), 1e-6, 1 - 1e-6)

    if y.shape != p.shape or y.size == 0:
        raise ValueError("y_true and p_up must be non-empty and the same length")
    if not 0.0 <= train_base_rate <= 1.0:
        raise ValueError("train_base_rate must be within [0, 1]")

    base = np.full_like(p, np.clip(train_base_rate, 1e-6, 1 - 1e-6))

    def brier(prob: np.ndarray) -> float:
        return float(np.mean((prob - y) ** 2))

    def log_loss(prob: np.ndarray) -> float:
        return float(-np.mean(y * np.log(prob) + (1 - y) * np.log(1 - prob)))

    majority = 1.0 if train_base_rate >= 0.5 else 0.0
    brier_model, brier_base = brier(p), brier(base)

    auc: Optional[float] = None
    if len(np.unique(y)) == 2:
        from sklearn.metrics import roc_auc_score
        auc = float(roc_auc_score(y, p))

    return {
        "n": int(y.size),
        "test_up_rate": round(float(y.mean()), 4),
        "accuracy": round(float(np.mean((p >= 0.5) == (y == 1.0))), 4),
        "baseline_accuracy": round(float(np.mean(y == majority)), 4),
        "brier": round(brier_model, 4),
        "baseline_brier": round(brier_base, 4),
        "brier_skill_score": round(1.0 - brier_model / brier_base, 4) if brier_base > 0 else None,
        "log_loss": round(log_loss(p), 4),
        "baseline_log_loss": round(log_loss(base), 4),
        "roc_auc": round(auc, 4) if auc is not None else None,
    }
