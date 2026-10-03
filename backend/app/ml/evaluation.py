"""
Volatility Forecasting — Metrics and Baselines

Provided so that "the ML model works" becomes a checkable claim rather
than an assertion. A volatility forecast is only interesting relative to
a baseline, because volatility is strongly persistent: predicting that
next month looks like this month is already a good forecast, and plenty
of models fail to beat it.

Use `compare_forecasts` to produce the table that belongs in the report.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Sequence

import numpy as np
import pandas as pd

from app.ml.config import HORIZON_DAYS, TRADING_DAYS_PER_YEAR

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
#  Metrics
# ─────────────────────────────────────────────────────────────────────

def rmse(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Root mean squared error, in annualised volatility units."""
    a, p = _clean_pair(actual, predicted)
    return float(np.sqrt(np.mean((a - p) ** 2)))


def mae(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Mean absolute error, in annualised volatility units."""
    a, p = _clean_pair(actual, predicted)
    return float(np.mean(np.abs(a - p)))


def r2(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """
    Coefficient of determination against the mean of the actuals.

    Reported for familiarity, but note that it flatters persistent
    series: a high R-squared here does not mean the model beat naive
    persistence. Judge by the baseline comparison, not by this.
    """
    a, p = _clean_pair(actual, predicted)
    ss_res = np.sum((a - p) ** 2)
    ss_tot = np.sum((a - np.mean(a)) ** 2)
    return float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")


def qlike(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """
    QLIKE loss, the standard asymmetric loss for volatility forecasts.

    Computed on VARIANCES (the inputs are volatilities and are squared
    internally), in the zero-anchored form:

        QLIKE = mean( s/h - ln(s/h) - 1 ),    s = actual var, h = forecast var

    This is non-negative and exactly 0 for a perfect forecast. It differs
    from Patton's `ln(h) + s/h` only by a term that depends on the
    realisation and not the forecast, so rankings on a given test set are
    identical while this version is easier to read.

    Why QLIKE and not just RMSE: it penalises under-forecasting risk far
    more than over-forecasting it. Halving the true variance costs much
    more than doubling it. For a risk tool that is the correct asymmetry
    — understating tail risk is the expensive mistake.
    """
    a, p = _clean_pair(actual, predicted)

    # Forecasts must be strictly positive to be admissible here
    valid = p > 0
    if not np.all(valid):
        logger.warning(
            "qlike: dropping %d non-positive forecasts", int((~valid).sum())
        )
        a, p = a[valid], p[valid]

    if a.size == 0:
        return float("nan")

    s, h = a ** 2, p ** 2
    ratio = s / h
    return float(np.mean(ratio - np.log(ratio) - 1.0))


def _clean_pair(actual: Sequence[float], predicted: Sequence[float]):
    """Align to arrays and drop any pair where either side is missing."""
    a = np.asarray(actual, dtype=float).ravel()
    p = np.asarray(predicted, dtype=float).ravel()

    if a.shape != p.shape:
        raise ValueError(f"Shape mismatch: actual {a.shape} vs predicted {p.shape}")

    keep = np.isfinite(a) & np.isfinite(p)
    if not np.any(keep):
        raise ValueError("No finite actual/predicted pairs to score")

    return a[keep], p[keep]


def score(actual: Sequence[float], predicted: Sequence[float]) -> Dict[str, float]:
    """All metrics at once, for one forecast series."""
    return {
        "rmse": rmse(actual, predicted),
        "mae": mae(actual, predicted),
        "qlike": qlike(actual, predicted),
        "r2": r2(actual, predicted),
    }


# ─────────────────────────────────────────────────────────────────────
#  Baselines
# ─────────────────────────────────────────────────────────────────────

def naive_persistence(table: pd.DataFrame) -> pd.Series:
    """
    "Next month's volatility equals this month's."

    Forecast = trailing 21-day realised volatility, i.e. the `rv_21`
    feature used unchanged. This is the baseline to beat; a model that
    does not beat it has not earned a place in the product.
    """
    if "rv_21" not in table.columns:
        raise ValueError("naive_persistence needs an 'rv_21' column")
    return table["rv_21"].rename("naive_persistence")


def fit_har(train: pd.DataFrame, target_column: str):
    """
    Fit a HAR-style linear model on realised volatility at 3 horizons.

    The HAR (Heterogeneous AutoRegressive) specification regresses future
    volatility on short, medium and long trailing realised volatility.
    It is a famously strong baseline — frequently competitive with far
    more complex models — so it belongs in the comparison rather than
    being quietly omitted.

    Returns:
        Fitted sklearn LinearRegression over ['rv_5', 'rv_21', 'rv_63'].
    """
    from sklearn.linear_model import LinearRegression

    cols = ["rv_5", "rv_21", "rv_63"]
    missing = [c for c in cols if c not in train.columns]
    if missing:
        raise ValueError(f"fit_har needs columns {missing}")

    frame = train[cols + [target_column]].dropna()
    model = LinearRegression().fit(frame[cols], frame[target_column])
    return model


def predict_har(model, table: pd.DataFrame) -> pd.Series:
    """Apply a model fitted by `fit_har`."""
    cols = ["rv_5", "rv_21", "rv_63"]
    return pd.Series(
        model.predict(table[cols]), index=table.index, name="har"
    )


def garch_forecast(
    close: pd.Series,
    horizon: int = HORIZON_DAYS,
    rescale_pct: bool = True,
) -> float:
    """
    One GARCH(1,1) forecast of mean annualised volatility over `horizon`.

    Fits on the full supplied return series and averages the predicted
    daily variance across the horizon.

    Note on scale: `arch` is numerically happier with percentage returns,
    so returns are multiplied by 100 before fitting and the resulting
    volatility is divided by 100 afterwards.

    Returns:
        Annualised volatility forecast. NaN if fitting fails.
    """
    try:
        from arch import arch_model
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "GARCH baseline needs the 'arch' package: pip install arch"
        ) from exc

    log_ret = np.log(close / close.shift(1)).dropna()
    if len(log_ret) < 250:
        return float("nan")

    scale = 100.0 if rescale_pct else 1.0

    try:
        fitted = arch_model(
            log_ret * scale, vol="Garch", p=1, q=1, mean="Constant", dist="normal"
        ).fit(disp="off", show_warning=False)

        forecast = fitted.forecast(horizon=horizon, reindex=False)
        mean_daily_var = float(np.mean(forecast.variance.values[-1, :]))
        daily_vol = np.sqrt(mean_daily_var) / scale
        return float(daily_vol * np.sqrt(TRADING_DAYS_PER_YEAR))
    except Exception as exc:  # noqa: BLE001 - arch fails in many ways
        logger.warning("GARCH fit failed: %s", exc)
        return float("nan")


def garch_forecast_series(
    close: pd.Series,
    eval_index: pd.DatetimeIndex,
    horizon: int = HORIZON_DAYS,
    refit_every: int = 21,
    min_history: int = 500,
) -> pd.Series:
    """
    Walk-forward GARCH(1,1) forecasts across an evaluation index.

    Refits periodically rather than daily — a daily refit over ten years
    of ten tickers takes hours and moves the forecast very little. The
    fitted parameters are reused until the next refit, while each date
    still only ever sees returns up to and including itself.

    Args:
        close: full close-price series (must cover `eval_index`)
        eval_index: dates to produce forecasts for
        horizon: forecast horizon in trading days
        refit_every: refit cadence in rows
        min_history: minimum observations before the first fit

    Returns:
        Series of annualised volatility forecasts aligned to `eval_index`.
        Slow: expect roughly `len(eval_index) / refit_every` model fits.
    """
    ordered = close.sort_index()
    out = pd.Series(index=eval_index, dtype=float, name="garch")

    last_value = float("nan")
    for i, date in enumerate(eval_index):
        if i % refit_every == 0:
            window = ordered.loc[:date]
            last_value = (
                garch_forecast(window, horizon=horizon)
                if len(window) >= min_history
                else float("nan")
            )
        out.loc[date] = last_value

    return out


# ─────────────────────────────────────────────────────────────────────
#  Comparison
# ─────────────────────────────────────────────────────────────────────

def compare_forecasts(
    actual: pd.Series,
    forecasts: Dict[str, pd.Series],
    baseline_name: str = "naive_persistence",
) -> pd.DataFrame:
    """
    Score several forecasts side by side against the same actuals.

    Args:
        actual: realised forward volatility (the target)
        forecasts: name -> forecast series, each aligned to `actual`
        baseline_name: key in `forecasts` to measure improvement against

    Returns:
        DataFrame indexed by forecast name with rmse / mae / qlike / r2,
        plus `rmse_vs_baseline` and `qlike_vs_baseline` as percentage
        improvements (positive = better than the baseline). Sorted by
        QLIKE, the loss that matters most for a risk tool.
    """
    rows: Dict[str, Dict[str, float]] = {}

    for name, series in forecasts.items():
        joined = pd.concat([actual.rename("actual"), series.rename("pred")], axis=1).dropna()
        if joined.empty:
            logger.warning("No overlapping rows for forecast '%s'; skipping", name)
            continue
        rows[name] = score(joined["actual"], joined["pred"])

    if not rows:
        raise ValueError("No forecast could be scored against the actuals")

    frame = pd.DataFrame(rows).T

    if baseline_name in frame.index:
        base_rmse = frame.loc[baseline_name, "rmse"]
        base_qlike = frame.loc[baseline_name, "qlike"]
        frame["rmse_vs_baseline"] = (1 - frame["rmse"] / base_rmse) * 100
        frame["qlike_vs_baseline"] = (1 - frame["qlike"] / base_qlike) * 100
    else:
        logger.warning(
            "Baseline '%s' not among forecasts; improvement columns omitted",
            baseline_name,
        )

    return frame.sort_values("qlike")
