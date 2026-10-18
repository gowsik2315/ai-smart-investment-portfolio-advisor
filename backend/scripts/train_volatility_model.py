"""
Train and (conditionally) save the volatility model described in
backend/app/ml/README.md.

Usage (from backend/):
    venv/Scripts/python.exe scripts/train_volatility_model.py --dry-run
    venv/Scripts/python.exe scripts/train_volatility_model.py --dry-run --garch
    venv/Scripts/python.exe scripts/train_volatility_model.py            # saves only if accepted
    venv/Scripts/python.exe scripts/train_volatility_model.py --force-save

What it does, in order
    1. Builds the panel ONLY from app.ml (load_history + build_training_table).
    2. Splits chronologically and VERIFIES the embargo in distinct trading
       dates, not rows; re-splits by date if the gap is under EMBARGO_DAYS.
    3. Tunes on walk-forward folds built by DATE inside the training half,
       with the same embargo between each fold's train and validation. The
       test set is not touched until the model has been selected.
    4. Candidates (Ridge, HistGradientBoosting, RandomForest) are fitted on
       log(volatility) via TransformedTargetRegressor(np.log, np.exp), so
       predictions are annualised volatility and can never be negative.
    5. Scores the selected model on the test half against naive persistence,
       HAR and (with --garch) GARCH(1,1).
    6. Saves through app.ml.model_registry.save_model ONLY if it beats naive
       persistence on BOTH RMSE and QLIKE.

Nothing defined in this file is ever pickled: the pipelines contain only
scikit-learn classes and numpy's log/exp, so the backend can unpickle the
artifact without importing this script.
"""

from __future__ import annotations

import argparse
import logging
import pickle
import platform
import re
import sys
import time
import warnings
from datetime import datetime, timezone
from functools import partial
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy  # noqa: E402
import sklearn  # noqa: E402
from sklearn.compose import TransformedTargetRegressor  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from app.ml.config import (  # noqa: E402
    EMBARGO_DAYS,
    HISTORY_PERIOD,
    INDEX_TICKER,
    MAX_PLAUSIBLE_VOLATILITY,
    MIN_PLAUSIBLE_VOLATILITY,
    TARGET_COLUMN,
    TRAINING_TICKERS,
)
from app.ml.data import PriceDataError, load_history  # noqa: E402
from app.ml.evaluation import (  # noqa: E402
    compare_forecasts,
    fit_har,
    garch_forecast_series,
    naive_persistence,
    predict_har,
    qlike,
    rmse,
)
from app.ml.features import (  # noqa: E402
    FEATURE_NAMES,
    build_training_table,
    chronological_split,
)
from app.ml.model_registry import load_model, save_model  # noqa: E402

RANDOM_STATE = 0
RIDGE_ALPHAS = [1, 10, 100, 1000, 3000, 10000, 30000, 100000, 300000]
FAMILIES = ["ridge", "hist_gb", "random_forest"]

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def fmt4(value) -> str:
    return f"{value:.4f}"


def fmt4_signed(value) -> str:
    return f"{value:+.4f}"


def show(frame: pd.DataFrame, **fmt) -> None:
    with pd.option_context("display.width", 200, "display.max_columns", 30):
        print(frame.to_string(**fmt))


# ---------------------------------------------------------------------------
# 8. Environment: the artifact is a pickle, so the serving env must match
# ---------------------------------------------------------------------------

def parse_requirements(path: Path) -> dict:
    pins = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_.\-]+)\s*==\s*([^\s;#]+)", line)
        if match:
            pins[match.group(1).lower().replace("_", "-")] = match.group(2)
    return pins


def check_environment() -> bool:
    """Print library versions against requirements.txt. True if all match."""
    section("Environment (the artifact is a pickle: serving must match training)")
    pins = parse_requirements(BACKEND_DIR / "requirements.txt")
    installed = {
        "scikit-learn": sklearn.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "joblib": joblib.__version__,
        "scipy": scipy.__version__,
    }

    print(f"python        {platform.python_version()}")
    ok = True
    for name, version in installed.items():
        pinned = pins.get(name)
        if pinned is None:
            status = "not pinned in requirements.txt"
        elif pinned == version:
            status = f"matches requirements.txt ({pinned})"
        else:
            status = f"MISMATCH: requirements.txt pins {pinned}"
            ok = False
        print(f"{name:<13} {version:<10} {status}")

    if not ok:
        print()
        print("WARNING: the training environment differs from requirements.txt. A pickle")
        print("written here may not load, or may behave differently, where the backend")
        print("runs. Saving is blocked unless --force-save is given.")
    return ok


# ---------------------------------------------------------------------------
# 1. Data: app.ml only
# ---------------------------------------------------------------------------

def build_panel(period: str, refresh: bool):
    """One date-sorted panel built exclusively through app.ml."""
    section("1. Data and features (app.ml only)")

    try:
        index_px = load_history(INDEX_TICKER, period=period, refresh=refresh)
    except PriceDataError as exc:
        sys.exit(f"ABORT: index history {INDEX_TICKER} unavailable: {exc}")

    histories, frames = {}, []
    for ticker in TRAINING_TICKERS:
        try:
            px = load_history(ticker, period=period, refresh=refresh)
        except PriceDataError as exc:
            # A silently smaller universe would make the stored metrics
            # describe a different training set than the README states.
            sys.exit(f"ABORT: {ticker} unavailable ({exc}). Not training on a reduced universe.")
        histories[ticker] = px
        table = build_training_table(px, index_px, ticker=ticker)
        frames.append(table)
        print(f"  {ticker:<14} {len(table):>5} rows  {table.index.min().date()} -> {table.index.max().date()}")

    panel = pd.concat(frames)
    panel.index.name = "date"
    # Keep ONLY the 21 features, the volatility label and the ticker tag.
    # build_training_table also carries the direction label; it is a future
    # quantity and must never reach a volatility model.
    panel = panel[FEATURE_NAMES + [TARGET_COLUMN, "ticker"]]
    panel = (
        panel.reset_index()
        .sort_values(["date", "ticker"], kind="stable")
        .set_index("date")
    )

    assert not panel[FEATURE_NAMES + [TARGET_COLUMN]].isna().any().any(), "panel has NaNs"
    nonpositive = int((panel[TARGET_COLUMN] <= 0).sum())
    assert nonpositive == 0, (
        f"{nonpositive} rows have a non-positive volatility target; log() would fail"
    )

    n_dates = panel.index.nunique()
    print()
    print(f"panel: {len(panel):,} rows x {len(FEATURE_NAMES)} features, {panel['ticker'].nunique()} tickers, "
          f"{n_dates:,} distinct dates, {panel.index.min().date()} -> {panel.index.max().date()}")
    print(f"rows per date: median {panel.groupby(level=0).size().median():.0f}")
    print(f"target {TARGET_COLUMN}: min {panel[TARGET_COLUMN].min():.4f}  median {panel[TARGET_COLUMN].median():.4f}  "
          f"max {panel[TARGET_COLUMN].max():.4f}")
    return panel, histories


# ---------------------------------------------------------------------------
# 2. Split with a VERIFIED embargo, measured in distinct trading dates
# ---------------------------------------------------------------------------

def date_gap(unique_dates: pd.DatetimeIndex, last_a, first_b) -> int:
    """Distinct trading dates strictly between two dates."""
    pos = unique_dates.get_indexer([last_a, first_b])
    if (pos < 0).any():
        raise ValueError("date not found in the panel's date axis")
    return int(pos[1] - pos[0] - 1)


def split_by_date(panel: pd.DataFrame, test_fraction: float, embargo: int):
    """Chronological split that drops `embargo` distinct DATES between halves."""
    dates = panel.index.unique().sort_values()
    n_test = int(len(dates) * test_fraction)
    test_start_pos = len(dates) - n_test
    train_end_pos = test_start_pos - embargo - 1
    train = panel.loc[panel.index <= dates[train_end_pos]]
    test = panel.loc[panel.index >= dates[test_start_pos]]
    return train, test


def split_panel(panel: pd.DataFrame, test_fraction: float):
    section("2. Chronological split and embargo verification")
    all_dates = panel.index.unique().sort_values()

    train, test = chronological_split(panel, test_fraction=test_fraction)
    last_train, first_test = train.index.max(), test.index.min()
    gap = date_gap(all_dates, last_train, first_test)
    rows_dropped = len(panel) - len(train) - len(test)
    per_date = len(panel) / len(all_dates)

    print(f"chronological_split(test_fraction={test_fraction}, embargo={EMBARGO_DAYS}):")
    print(f"  last train date {last_train.date()}   first test date {first_test.date()}")
    print(f"  rows dropped between the halves : {rows_dropped}")
    print(f"  distinct trading dates between  : {gap}   (required >= {EMBARGO_DAYS})")
    print(f"  panel stacks {per_date:.1f} rows per date, so a {EMBARGO_DAYS}-ROW embargo would "
          f"span only ~{EMBARGO_DAYS / per_date:.1f} dates")

    if gap < EMBARGO_DAYS:
        print()
        print(f"  GAP TOO SMALL ({gap} < {EMBARGO_DAYS}): chronological_split embargoed by rows.")
        print("  Re-splitting by date.")
        train, test = split_by_date(panel, test_fraction, EMBARGO_DAYS)
        last_train, first_test = train.index.max(), test.index.min()
        gap = date_gap(all_dates, last_train, first_test)
        print(f"  after re-split: {gap} distinct dates between {last_train.date()} and {first_test.date()}")
    else:
        print(f"  -> embargoes by DATES (drops {EMBARGO_DAYS} dates x {per_date:.0f} tickers); no re-split needed.")

    assert gap >= EMBARGO_DAYS, f"embargo is {gap} dates, need >= {EMBARGO_DAYS}"
    assert last_train < first_test, "train and test overlap in time"
    assert len(train) + len(test) <= len(panel)

    print()
    print(f"train: {len(train):,} rows  {train.index.min().date()} -> {last_train.date()}  "
          f"({train.index.nunique():,} dates)")
    print(f"test : {len(test):,} rows  {first_test.date()} -> {test.index.max().date()}  "
          f"({test.index.nunique():,} dates)")
    print(f"final embargo gap: {gap} distinct trading dates  [asserted >= {EMBARGO_DAYS}]")
    return train, test, gap


# ---------------------------------------------------------------------------
# 3. Walk-forward folds by DATE inside the training half
# ---------------------------------------------------------------------------

def date_folds(train: pd.DataFrame, n_folds: int, embargo: int, min_train_frac: float = 0.4):
    """
    Expanding-window folds built on the date axis. Fold k trains on every date
    up to (validation start - embargo) and validates on a contiguous block of
    dates, so a ticker's rows can never straddle the train/validation boundary
    the way they would with a row-based TimeSeriesSplit on a pooled panel.
    """
    dates = train.index.unique().sort_values()
    n = len(dates)
    start = int(n * min_train_frac)
    block = (n - start) // n_folds
    if block < 30:
        sys.exit(f"ABORT: only {block} dates per validation block; use fewer --folds")

    folds = []
    for k in range(n_folds):
        v0 = start + k * block
        v1 = start + (k + 1) * block if k < n_folds - 1 else n
        t_end = v0 - embargo                      # train = dates[:t_end]
        tr_dates, va_dates = dates[:t_end], dates[v0:v1]

        gap = date_gap(dates, tr_dates[-1], va_dates[0])
        assert gap >= embargo, f"fold {k}: embargo {gap} < {embargo}"
        assert tr_dates[-1] < va_dates[0]
        folds.append({
            "train": train.loc[train.index.isin(tr_dates)],
            "val": train.loc[train.index.isin(va_dates)],
            "gap": gap,
            "tr_range": (tr_dates[0], tr_dates[-1]),
            "va_range": (va_dates[0], va_dates[-1]),
        })
    return folds


# ---------------------------------------------------------------------------
# 4. Candidates: all fitted on log(volatility); only np.log / np.exp inside
# ---------------------------------------------------------------------------

def wrap(regressor):
    return TransformedTargetRegressor(regressor=regressor, func=np.log, inverse_func=np.exp)


def make_ridge(alpha):
    return wrap(Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=alpha))]))


def make_hist_gb(max_depth, max_iter):
    # early_stopping=False on purpose: scikit-learn's default carves a RANDOM
    # 10% validation split out of the training rows, which on overlapping
    # 21-day targets leaks neighbouring rows into the stopping decision.
    return wrap(HistGradientBoostingRegressor(
        learning_rate=0.05, max_depth=max_depth, max_iter=max_iter,
        min_samples_leaf=300, l2_regularization=10.0,
        early_stopping=False, random_state=RANDOM_STATE,
    ))


def make_random_forest(max_depth, min_samples_leaf):
    return wrap(RandomForestRegressor(
        n_estimators=200, max_depth=max_depth, min_samples_leaf=min_samples_leaf,
        max_features=0.5, n_jobs=-1, random_state=RANDOM_STATE,
    ))


def candidate_grid(family: str):
    """(params dict, zero-argument factory) pairs for one family."""
    if family == "ridge":
        return [({"alpha": a}, partial(make_ridge, a)) for a in RIDGE_ALPHAS]
    if family == "hist_gb":
        return [
            ({"max_depth": d, "max_iter": it}, partial(make_hist_gb, d, it))
            for d in (2, 3) for it in (100, 300)
        ]
    if family == "random_forest":
        return [
            ({"max_depth": d, "min_samples_leaf": leaf}, partial(make_random_forest, d, leaf))
            for d in (4, 8) for leaf in (100, 400)
        ]
    raise ValueError(family)


def cross_validate(family: str, folds):
    """Walk-forward CV for every parameter set in one family; selection on QLIKE."""
    results = []
    for params, factory in candidate_grid(family):
        q, r = [], []
        for fold in folds:
            tr, va = fold["train"], fold["val"]
            est = factory().fit(tr[FEATURE_NAMES], tr[TARGET_COLUMN])
            pred = est.predict(va[FEATURE_NAMES])
            q.append(qlike(va[TARGET_COLUMN], pred))
            r.append(rmse(va[TARGET_COLUMN], pred))
        results.append({
            "family": family, "params": params, "factory": factory,
            "qlike_mean": float(np.mean(q)), "qlike_std": float(np.std(q)),
            "rmse_mean": float(np.mean(r)), "qlike_folds": q,
        })
    return results


def cv_qlike_of(result: dict) -> float:
    return result["qlike_mean"]


def baseline_cv_reference(folds):
    """Naive persistence and HAR on the same folds, for context only."""
    out = {"naive_persistence": [], "har": []}
    for fold in folds:
        tr, va = fold["train"], fold["val"]
        y = va[TARGET_COLUMN]
        out["naive_persistence"].append(qlike(y, naive_persistence(va)))
        out["har"].append(qlike(y, predict_har(fit_har(tr, TARGET_COLUMN), va)))
    return out


def select_family(best: dict, n_folds: int):
    """
    One-standard-error rule: take the SIMPLEST family whose cross-validated
    QLIKE is within one standard error of the best family's.

    When candidates are separated by less than the fold-to-fold noise,
    picking the nominal winner is picking noise; the simpler model is the one
    more likely to hold up out of sample. FAMILIES is ordered simplest first.
    """
    cv = {family: best[family]["qlike_mean"] for family in FAMILIES}
    lowest = min(cv, key=cv.get)
    # qlike_std is the population std over folds; this is std / sqrt(n_folds)
    # with the n-1 correction, i.e. the standard error of the mean.
    se = best[lowest]["qlike_std"] / np.sqrt(n_folds - 1)
    threshold = cv[lowest] + se
    within = [family for family in FAMILIES if cv[family] <= threshold]
    return within[0], lowest, se, threshold, within


def tune(train: pd.DataFrame, n_folds: int, model_choice: str):
    section(f"3. Tuning: walk-forward folds by DATE ({n_folds} folds, {EMBARGO_DAYS}-date embargo, select on QLIKE)")
    folds = date_folds(train, n_folds, EMBARGO_DAYS)

    rows = [{
        "fold": k, "train_dates": f"{f['tr_range'][0].date()}..{f['tr_range'][1].date()}",
        "val_dates": f"{f['va_range'][0].date()}..{f['va_range'][1].date()}",
        "gap_dates": f["gap"], "train_rows": len(f["train"]), "val_rows": len(f["val"]),
    } for k, f in enumerate(folds)]
    show(pd.DataFrame(rows).set_index("fold"))
    print(f"(every fold's embargo asserted >= {EMBARGO_DAYS} distinct dates; test set not used)")

    best = {}
    for family in FAMILIES:
        t0 = time.time()
        results = cross_validate(family, folds)
        best[family] = min(results, key=cv_qlike_of)
        print(f"\n[{family}]  {len(results)} candidates, {time.time() - t0:.0f}s")
        table = pd.DataFrame([{
            "params": str(r["params"]), "cv_qlike": r["qlike_mean"], "qlike_std": r["qlike_std"],
            "cv_rmse": r["rmse_mean"],
            "chosen": "<--" if r is best[family] else "",
        } for r in results])
        show(table, index=False, float_format=fmt4)

    # Ridge alpha at the edge of the grid means the grid is clipping the optimum
    ridge_alpha = best["ridge"]["params"]["alpha"]
    if ridge_alpha in (RIDGE_ALPHAS[0], RIDGE_ALPHAS[-1]):
        side = "LOWEST" if ridge_alpha == RIDGE_ALPHAS[0] else "HIGHEST"
        print(f"\nWARNING: the chosen Ridge alpha ({ridge_alpha}) is the {side} value in the grid "
              f"{RIDGE_ALPHAS}. The true optimum may lie beyond it; widen the grid before trusting it.")

    ref = baseline_cv_reference(folds)
    summary = [{
        "model": f"{fam} {best[fam]['params']}", "cv_qlike": best[fam]["qlike_mean"],
        "qlike_std": best[fam]["qlike_std"], "cv_rmse": best[fam]["rmse_mean"],
    } for fam in FAMILIES]
    summary += [{"model": f"{k} (reference, not selectable)", "cv_qlike": float(np.mean(v)),
                 "qlike_std": float(np.std(v)), "cv_rmse": float("nan")} for k, v in ref.items()]
    print("\nCross-validated QLIKE, lower is better (validation folds only):")
    show(pd.DataFrame(summary).set_index("model"), float_format=fmt4)

    picked, lowest, se, threshold, within = select_family(best, n_folds)
    print(f"\nlowest cross-validated QLIKE: {lowest} {best[lowest]['qlike_mean']:.4f}  "
          f"(standard error {se:.4f}, so the one-SE threshold is {threshold:.4f})")
    print(f"families within one standard error of it: {', '.join(within)}")
    if model_choice == "auto":
        chosen = picked
        why = ("the best family" if picked == lowest else
               f"the simplest family within one standard error of {lowest}; "
               f"the difference is smaller than the noise")
        print(f"selected: {chosen} {best[chosen]['params']}  ({why})")
    else:
        chosen = model_choice
        print(f"selected: {chosen} {best[chosen]['params']}  (forced by --model)")
    return best, chosen


# ---------------------------------------------------------------------------
# 5. Test-set evaluation against all baselines
# ---------------------------------------------------------------------------

def to_unique_index(frame: pd.DataFrame) -> pd.DataFrame:
    """(date, ticker) index: unique, so forecasts can be joined safely."""
    out = frame.copy()
    out.index = pd.MultiIndex.from_arrays([frame.index, frame["ticker"].to_numpy()], names=["date", "ticker"])
    assert out.index.is_unique, "duplicate (date, ticker) rows"
    return out


def run_garch(test_e: pd.DataFrame, histories: dict, refit_every: int) -> pd.Series:
    """
    garch_forecast_series takes ONE close series and an eval index, so it is run
    per ticker on that ticker's own history and its own test dates, then aligned
    back onto the panel's (date, ticker) rows.
    """
    print(f"\nGARCH(1,1) walk-forward, refit every {refit_every} rows, per ticker:")
    parts = []
    for ticker in TRAINING_TICKERS:
        t0 = time.time()
        dates = test_e.xs(ticker, level="ticker").index.sort_values()
        series = garch_forecast_series(
            histories[ticker]["close"], pd.DatetimeIndex(dates), refit_every=refit_every,
        )
        parts.append(pd.Series(
            series.to_numpy(),
            index=pd.MultiIndex.from_arrays([series.index, [ticker] * len(series)], names=["date", "ticker"]),
        ))
        print(f"  {ticker:<14} {len(series):>4} dates, {series.isna().sum()} NaN, {time.time() - t0:.0f}s")
    return pd.concat(parts).rename("garch")


def evaluate(train, test, model, histories, use_garch: bool, garch_refit: int):
    section("4. Test-set evaluation (selected model vs baselines)")
    test_e = to_unique_index(test)
    actual = test_e[TARGET_COLUMN].rename("actual")

    forecasts = {
        "naive_persistence": naive_persistence(test_e),
        "har": predict_har(fit_har(train, TARGET_COLUMN), test_e),
        "model": pd.Series(model.predict(test_e[FEATURE_NAMES]), index=test_e.index, name="model"),
    }
    if use_garch:
        forecasts["garch"] = run_garch(test_e, histories, garch_refit)
    else:
        print("GARCH baseline skipped (use --garch to include it).")

    # Score every forecast on the SAME rows: compare_forecasts drops rows per
    # series, which would otherwise score GARCH on fewer rows than naive.
    frame = pd.concat([actual] + list(forecasts.values()), axis=1)
    forecast_cols = list(forecasts)
    usable = (
        np.isfinite(frame[["actual"] + forecast_cols]).all(axis=1)
        & (frame[forecast_cols] > 0).all(axis=1)
    )
    dropped = int((~usable).sum())
    print(f"\nscored on {int(usable.sum()):,} of {len(frame):,} test rows "
          f"(common support: finite and positive for every forecast; {dropped} dropped)")
    if dropped:
        for col in forecast_cols:
            bad = int((~(np.isfinite(frame[col]) & (frame[col] > 0))).sum())
            if bad:
                print(f"    {col}: {bad} unusable rows")

    frame = frame[usable]
    table = compare_forecasts(
        frame["actual"], {name: frame[name] for name in forecast_cols}, baseline_name="naive_persistence",
    )
    print()
    show(table, float_format=fmt4)
    print("\nrmse_vs_baseline / qlike_vs_baseline are % improvement over naive persistence (positive = better).")
    return table, frame, test_e


# ---------------------------------------------------------------------------
# 6. Acceptance
# ---------------------------------------------------------------------------

def acceptance(table: pd.DataFrame):
    section("5. Acceptance: must beat naive persistence on BOTH RMSE and QLIKE")
    m, n = table.loc["model"], table.loc["naive_persistence"]
    beats_rmse, beats_qlike = m["rmse"] < n["rmse"], m["qlike"] < n["qlike"]

    print(f"RMSE : model {m['rmse']:.4f} vs naive {n['rmse']:.4f}  -> {'beats' if beats_rmse else 'DOES NOT beat'} "
          f"({m['rmse_vs_baseline']:+.1f}%)")
    print(f"QLIKE: model {m['qlike']:.4f} vs naive {n['qlike']:.4f}  -> {'beats' if beats_qlike else 'DOES NOT beat'} "
          f"({m['qlike_vs_baseline']:+.1f}%)")

    reasons = []
    if not beats_rmse:
        reasons.append("does not beat naive persistence on RMSE")
    if not beats_qlike:
        reasons.append("does not beat naive persistence on QLIKE")

    # Beating naive is the bar for saving; HAR and GARCH are the honest context.
    for name in ("har", "garch"):
        if name in table.index:
            b = table.loc[name]
            wins = (m["rmse"] < b["rmse"]) and (m["qlike"] < b["qlike"])
            print(f"vs {name.upper():<5}: RMSE {m['rmse'] - b['rmse']:+.4f}, QLIKE {m['qlike'] - b['qlike']:+.4f}  "
                  f"-> {'beats it on both' if wins else 'does NOT beat it on both (informational, not a save condition)'}")
    return not reasons, reasons


# ---------------------------------------------------------------------------
# 9. Diagnostics
# ---------------------------------------------------------------------------

def diagnostics(chosen: str, finals: dict, frame: pd.DataFrame):
    section(f"6. Diagnostics for the selected model ({chosen}), test rows")
    actual, pred = frame["actual"], frame["model"]

    desc = pd.DataFrame({
        "predicted": pred.describe(percentiles=[0.01, 0.5, 0.99]),
        "actual": actual.describe(percentiles=[0.01, 0.5, 0.99]),
    }).loc[["min", "1%", "50%", "mean", "99%", "max"]]
    print("Prediction range vs actual range (annualised volatility):")
    show(desc, float_format=fmt4)
    print(f"\nmean predicted / mean actual = {pred.mean() / actual.mean():.3f}  "
          f"(below 1 means the model under-forecasts on average; QLIKE punishes that)")
    print(f"correlation: pearson {pred.corr(actual):.4f}   spearman {pred.corr(actual, method='spearman'):.4f}")

    outside = (pred < MIN_PLAUSIBLE_VOLATILITY) | (pred > MAX_PLAUSIBLE_VOLATILITY)
    print(f"\npredictions outside the service guard [{MIN_PLAUSIBLE_VOLATILITY:.0%}, {MAX_PLAUSIBLE_VOLATILITY:.0%}]: "
          f"{int(outside.sum())} of {len(pred)} ({outside.mean():.2%})   "
          f"[min {pred.min():.4f}, max {pred.max():.4f}]")

    deciles = pd.qcut(pred, 10, duplicates="drop")
    table = pd.DataFrame({"predicted": pred, "actual": actual, "naive_rv21": frame["naive_persistence"]})
    grouped = table.groupby(deciles, observed=True).agg(
        n=("predicted", "size"), mean_predicted=("predicted", "mean"),
        mean_actual=("actual", "mean"), mean_naive=("naive_rv21", "mean"),
    )
    grouped["actual/predicted"] = grouped["mean_actual"] / grouped["mean_predicted"]
    grouped.index = [f"D{i + 1}" for i in range(len(grouped))]
    print("\nDecile table (rows binned by predicted volatility, D1 = lowest):")
    show(grouped, float_format=fmt4)
    print("A calibrated model has actual/predicted near 1 in every decile and mean_actual rising with the decile.")

    ridge = finals["ridge"].regressor_.named_steps["ridge"]
    coefs = pd.DataFrame({"coef": ridge.coef_}, index=FEATURE_NAMES)
    coefs = coefs.reindex(coefs["coef"].abs().sort_values(ascending=False).index)
    print(f"\nRidge coefficients (alpha={ridge.alpha}, on STANDARDISED features, target = log volatility; "
          f"intercept {ridge.intercept_:.4f}):")
    show(coefs, float_format=fmt4_signed)


def assert_unpicklable_references_absent(model) -> None:
    """The backend must be able to unpickle the artifact without this script."""
    blob = pickle.dumps(model)
    assert b"__main__" not in blob, "estimator references __main__ and would not unpickle in the backend"
    pickle.loads(blob)


# ---------------------------------------------------------------------------
# 7. Save
# ---------------------------------------------------------------------------

def build_metrics(table, cv_best, n_train, n_test, gap) -> dict:
    metrics = {}
    for key in ("rmse", "mae", "qlike", "r2"):
        metrics[key] = float(table.loc["model", key])
        metrics[f"baseline_{key}"] = float(table.loc["naive_persistence", key])
    metrics["rmse_vs_naive_pct"] = float(table.loc["model", "rmse_vs_baseline"])
    metrics["qlike_vs_naive_pct"] = float(table.loc["model", "qlike_vs_baseline"])
    for name in ("har", "garch"):
        if name in table.index:
            for key in ("rmse", "mae", "qlike"):
                metrics[f"{name}_{key}"] = float(table.loc[name, key])
    metrics["cv_qlike_mean"] = cv_best["qlike_mean"]
    metrics["cv_qlike_std"] = cv_best["qlike_std"]
    metrics["n_train_rows"] = float(n_train)
    metrics["n_test_rows"] = float(n_test)
    metrics["embargo_gap_dates"] = float(gap)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="never save, whatever the result")
    parser.add_argument("--force-save", action="store_true",
                        help="save even if acceptance or the environment check fails (ignored with --dry-run)")
    parser.add_argument("--garch", action="store_true", help="include the GARCH(1,1) baseline (slow)")
    parser.add_argument("--garch-refit", type=int, default=21, help="GARCH refit cadence in rows (default 21)")
    parser.add_argument("--model", choices=["auto"] + FAMILIES, default="auto",
                        help="auto = simplest family within one standard error of the best cross-validated QLIKE")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--period", default=HISTORY_PERIOD)
    parser.add_argument("--refresh", action="store_true", help="re-download price history")
    parser.add_argument("--version", default=None, help="model_version to store")
    args = parser.parse_args()

    # Never let a non-ASCII character in a report crash the run on a Windows
    # console or a redirected stream. Done here, not at import, so importing
    # this module (as the tests do) has no side effects.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    warnings.filterwarnings("ignore", category=FutureWarning)
    started = time.time()

    env_ok = check_environment()
    panel, histories = build_panel(args.period, args.refresh)
    train, test, gap = split_panel(panel, args.test_fraction)

    best, chosen = tune(train, args.folds, args.model)

    # Final fits use the TRAINING HALF ONLY, so the stored metrics describe
    # exactly the artifact that gets saved.
    section("Final fits on the training half")
    finals = {}
    for family in FAMILIES:
        finals[family] = best[family]["factory"]().fit(train[FEATURE_NAMES], train[TARGET_COLUMN])
        print(f"  {family:<14} fitted on {len(train):,} rows  {best[family]['params']}")
    model = finals[chosen]
    assert_unpicklable_references_absent(model)
    print(f"\nselected: {chosen}. Pickle check passed: no reference to __main__ or to this script.")

    table, frame, test_e = evaluate(train, test, model, histories, args.garch, args.garch_refit)
    accepted, reasons = acceptance(table)
    diagnostics(chosen, finals, frame)

    # ----------------------------------------------------------------- decision
    section("7. Decision")
    metrics = build_metrics(table, best[chosen], len(train), len(frame), gap)
    blockers = list(reasons) + ([] if env_ok else ["training environment differs from requirements.txt"])

    if args.dry_run:
        print("DRY RUN: nothing saved." + (" --force-save ignored." if args.force_save else ""))
        print("Would save: " + ("YES" if not blockers else "NO (" + "; ".join(blockers) + ")"))
    elif blockers and not args.force_save:
        print("NOT SAVED. " + "; ".join(blockers) + ".")
        print("No artifact was written. Re-run with --force-save to override, or improve the model.")
    else:
        version = args.version or f"{chosen}-log-{datetime.now(timezone.utc):%Y%m%d}"
        notes = (
            f"{chosen} {best[chosen]['params']} on log(volatility) via TransformedTargetRegressor. "
            f"Trained {train.index.min().date()}..{train.index.max().date()}, "
            f"tested {test.index.min().date()}..{test.index.max().date()}, "
            f"embargo {gap} dates, {len(TRAINING_TICKERS)} tickers. "
            f"RMSE {metrics['rmse']:.4f} vs naive {metrics['baseline_rmse']:.4f} ({metrics['rmse_vs_naive_pct']:+.1f}%), "
            f"QLIKE {metrics['qlike']:.4f} vs naive {metrics['baseline_qlike']:.4f} ({metrics['qlike_vs_naive_pct']:+.1f}%). "
            f"sklearn {sklearn.__version__}, numpy {np.__version__}, pandas {pd.__version__}."
        )
        if blockers:
            notes += " FORCE-SAVED despite: " + "; ".join(blockers) + "."
            print("WARNING: --force-save used despite: " + "; ".join(blockers))

        path = save_model(model=model, model_version=version, metrics=metrics, notes=notes)
        print(f"SAVED {version} -> {path}")

        # Prove the contract end to end: strict load, then identical predictions.
        artifact = load_model(path, strict=True)
        sample = test[FEATURE_NAMES].iloc[:5]
        assert np.allclose(model.predict(sample), [artifact.predict(sample.iloc[[i]]) for i in range(len(sample))])
        print("Reloaded with load_model(strict=True); predictions identical.")
        print("Next: POST /api/ml/reload-model (or restart the backend) to serve it.")

    print(f"\nfinished in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
