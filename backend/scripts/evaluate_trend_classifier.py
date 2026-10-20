"""
Can a classifier beat the historical base rate at 21-day direction?

This script exists to answer that question reproducibly, and to deploy a
model ONLY if the answer is yes. Its expected outcome is "no edge" — that
is a legitimate result, not a failure, and the Stock Predictor is built
to display the base rate honestly when it holds.

The bar is deliberately strict:

  1. The baseline is the TRAIN-period base rate, never 50%. Most large
     caps rise more often than they fall over a month, so beating a coin
     flip is not evidence of anything.
  2. Scoring is on Brier SKILL (a proper scoring rule applied to the
     probability), not accuracy. A model can be "right" 55% of the time
     while its probabilities are worthless.
  3. A model must beat the baseline by a margin whose 95% block-bootstrap
     interval excludes zero. A positive point estimate alone is noise.

Run from backend/:

    venv/Scripts/python.exe scripts/evaluate_trend_classifier.py
    venv/Scripts/python.exe scripts/evaluate_trend_classifier.py --save

Like the volatility script, this defines no lambdas and no classes, so a
saved artifact never references __main__ and can be unpickled by the API.
"""
from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime, timezone
from functools import partial
from operator import itemgetter
from pathlib import Path

import numpy as np
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sklearn.ensemble import (  # noqa: E402
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from app.ml.config import EMBARGO_DAYS, HORIZON_DAYS, TARGET_UP_COLUMN  # noqa: E402
from app.ml.features import FEATURE_NAMES  # noqa: E402
from app.ml.trend import evaluate_trend_probabilities  # noqa: E402
from app.ml.trend_registry import save_trend_model  # noqa: E402

warnings.filterwarnings("ignore")

DATASETS = BACKEND_DIR / "datasets"
RANDOM_STATE = 42
BOOTSTRAP_RESAMPLES = 2000


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def make_logistic(C: float):
    return Pipeline([("scale", StandardScaler()),
                     ("clf", LogisticRegression(C=C, max_iter=2000))])


def make_random_forest(max_depth: int, min_samples_leaf: int):
    return RandomForestClassifier(
        n_estimators=300, max_depth=max_depth, min_samples_leaf=min_samples_leaf,
        max_features=0.5, n_jobs=-1, random_state=RANDOM_STATE)


def make_hist_gb(max_depth: int, max_iter: int):
    # early_stopping=False: the default carves a RANDOM validation split,
    # which on overlapping 21-day labels leaks neighbouring rows.
    return HistGradientBoostingClassifier(
        learning_rate=0.03, max_depth=max_depth, max_iter=max_iter,
        min_samples_leaf=300, l2_regularization=10.0,
        early_stopping=False, random_state=RANDOM_STATE)


def candidates():
    """(name, zero-argument factory) pairs, simplest family first."""
    return [
        ("logistic C=0.01", partial(make_logistic, 0.01)),
        ("logistic C=0.1", partial(make_logistic, 0.1)),
        ("logistic C=1.0", partial(make_logistic, 1.0)),
        ("random forest d=5", partial(make_random_forest, 5, 200)),
        ("random forest d=8", partial(make_random_forest, 8, 100)),
        ("hist gb d=3", partial(make_hist_gb, 3, 200)),
        ("hist gb d=2", partial(make_hist_gb, 2, 300)),
    ]


def load_split():
    train_path, test_path = DATASETS / "trend_train.parquet", DATASETS / "trend_test.parquet"
    if not train_path.exists() or not test_path.exists():
        sys.exit(
            f"ABORT: {train_path.name} / {test_path.name} not found in {DATASETS}.\n"
            "Build them first:  python -m ml.prepare_trend_dataset"
        )
    return pd.read_parquet(train_path), pd.read_parquet(test_path)


def verify_embargo(train: pd.DataFrame, test: pd.DataFrame) -> int:
    """
    Distinct trading dates between the halves.

    Overlapping 21-day labels mean a gap smaller than the horizon lets a
    training row's outcome window reach into the test period. Measured in
    DATES, because on a pooled panel a gap of N rows spans only N/tickers
    dates.
    """
    last_train, first_test = train.index.max(), test.index.min()
    if last_train >= first_test:
        sys.exit("ABORT: train and test overlap in time")

    gap = len(pd.bdate_range(last_train, first_test)) - 2
    print(f"last train {last_train.date()}   first test {first_test.date()}")
    print(f"business days strictly between : {gap}   (need >= {EMBARGO_DAYS})")
    if gap < EMBARGO_DAYS:
        sys.exit(f"ABORT: embargo is {gap} days, need >= {EMBARGO_DAYS}")
    print("-> embargo satisfied; a training label cannot reach into the test half")
    return gap


def bootstrap_skill_interval(y_true, p_model, base_rate: float):
    """
    95% interval for Brier skill, resampling CONTIGUOUS 21-day blocks.

    Daily rows overlap and are strongly dependent, so an i.i.d. bootstrap
    would give intervals far too narrow and manufacture significance.
    """
    rng = np.random.default_rng(RANDOM_STATE)
    y = np.asarray(y_true, dtype=float)
    n, block = len(y), HORIZON_DAYS
    if n <= block:
        return float("nan"), float("nan")

    starts = np.arange(0, n - block)
    skills = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        picks = rng.choice(starts, size=max(1, n // block), replace=True)
        idx = np.concatenate([np.arange(s, s + block) for s in picks])
        idx = idx[idx < n]
        yb, pb = y[idx], p_model[idx]
        brier_model = np.mean((pb - yb) ** 2)
        brier_base = np.mean((np.full_like(pb, base_rate) - yb) ** 2)
        if brier_base > 0:
            skills.append(1.0 - brier_model / brier_base)

    return float(np.percentile(skills, 2.5)), float(np.percentile(skills, 97.5))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", action="store_true",
                        help="Save the winner IF it clears the acceptance bar")
    parser.add_argument("--force-save", action="store_true",
                        help="Save the best model even if it fails the bar (not for serving)")
    args = parser.parse_args()

    section("1. Data and leakage check")
    train, test = load_split()
    target = TARGET_UP_COLUMN if TARGET_UP_COLUMN in train.columns else "target_up_21d"
    features = [c for c in FEATURE_NAMES if c in train.columns]
    if len(features) != len(FEATURE_NAMES):
        sys.exit(f"ABORT: dataset has {len(features)} of {len(FEATURE_NAMES)} features")

    print(f"train {len(train):>7,} rows  {train.index.min().date()} -> {train.index.max().date()}")
    print(f"test  {len(test):>7,} rows  {test.index.min().date()} -> {test.index.max().date()}")
    print(f"features {len(features)}   target {target}")
    print()
    verify_embargo(train, test)

    X_train, y_train = train[features], train[target].astype(int)
    X_test, y_test = test[features], test[target].astype(int)
    base_rate = float(y_train.mean())

    section("2. The baseline that matters")
    print(f"TRAIN base rate (share of {HORIZON_DAYS}-day windows that rose): {base_rate:.4f}")
    print(f"TEST  base rate                                     : {y_test.mean():.4f}")
    print()
    print("A model must beat the TRAIN rate quoted as a constant forecast.")
    print("Beating 50% proves nothing: most large caps rise more often than not.")
    if abs(base_rate - y_test.mean()) > 0.05:
        print()
        print(f"NOTE: the regime shifted by {abs(base_rate - y_test.mean()):.1%} between the")
        print("halves. A model that learned 'things go up' will be over-optimistic.")

    section("3. Candidates, scored on the untouched test half")
    print(f"{'model':<22}{'Brier':>9}{'base':>9}{'skill':>10}{'AUC':>8}{'acc':>8}")
    print("-" * 78)

    results = []
    for name, factory in candidates():
        model = factory().fit(X_train, y_train)
        up_column = list(model.classes_).index(1)
        p_test = model.predict_proba(X_test)[:, up_column]
        metrics = evaluate_trend_probabilities(y_test, p_test, base_rate)
        results.append({"name": name, "model": model, "p": p_test,
                        "skill": metrics["brier_skill_score"], "metrics": metrics})
        print(f"{name:<22}{metrics['brier']:>9.4f}{metrics['baseline_brier']:>9.4f}"
              f"{metrics['brier_skill_score']:>+10.4f}"
              f"{(metrics['roc_auc'] or float('nan')):>8.3f}{metrics['accuracy']:>8.3f}")

    best = max(results, key=itemgetter("skill"))

    section("4. Is the best model's edge distinguishable from zero?")
    low, high = bootstrap_skill_interval(y_test, best["p"], base_rate)
    print(f"best model : {best['name']}")
    print(f"Brier skill: {best['skill']:+.4f}")
    print(f"95% block-bootstrap interval ({BOOTSTRAP_RESAMPLES} resamples, "
          f"{HORIZON_DAYS}-day blocks): {low:+.4f} to {high:+.4f}")
    print()
    print(f"predicted probabilities span {best['p'].min():.3f} to {best['p'].max():.3f} "
          f"(base rate {base_rate:.3f})")

    accepted = best["skill"] > 0 and low > 0

    section("5. Verdict")
    if accepted:
        print("ACCEPTED: the model beats the base rate and the interval excludes zero.")
    else:
        print("NO EDGE: the model does not beat the historical base rate.")
        print()
        print("This is the expected result and a legitimate finding. Direction over")
        print(f"{HORIZON_DAYS} trading days is close to unpredictable from price history")
        print("alone. The Stock Predictor therefore shows the stock's own base rate,")
        print("labelled 'Not a prediction', and puts its real value in the expected")
        print("PRICE RANGE, which is driven by the volatility model and does work.")

    if args.force_save and not accepted:
        print()
        print("--force-save given: saving a model that FAILED the bar. It must not be")
        print("presented as a validated predictor.")

    if (args.save and accepted) or args.force_save:
        version = f"trend-{best['name'].split()[0]}-{datetime.now(timezone.utc):%Y%m%d}"
        path = save_trend_model(
            model=best["model"],
            model_version=version,
            metrics=best["metrics"],
            notes=(f"{best['name']}; Brier skill {best['skill']:+.4f}; "
                   f"95% CI {low:+.4f} to {high:+.4f}; "
                   f"{'accepted' if accepted else 'FORCE-SAVED, failed acceptance'}"),
            feature_names=features,
        )
        print(f"\nsaved -> {path}")
    elif args.save:
        print("\n--save given but the model was not accepted; nothing written.")
        print("The app keeps showing the base rate, which is the honest default.")


if __name__ == "__main__":
    main()
