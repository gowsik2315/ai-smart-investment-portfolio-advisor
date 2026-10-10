"""
Build the stock-trend training dataset.

Downloads price history for the training universe, builds the shared
features and the 21-day up/down label, and writes a panel to disk ready
for fitting a classifier.

Like `prepare_volatility_dataset.py`, this stops short of training. What it
guarantees is that whatever you fit is fitted on features built by the same
code the API uses at inference time (`app.ml.features.build_features`).

Usage
-----
    cd backend
    venv/Scripts/python.exe -m ml.prepare_trend_dataset
    venv/Scripts/python.exe -m ml.prepare_trend_dataset --refresh

Outputs (under backend/datasets/)
---------------------------------
    trend_panel.parquet   features + target_up_21d + ticker, all tickers
    trend_train.parquet   chronological training split
    trend_test.parquet    held-out test split, after the embargo
    trend_report.txt      class balance, baseline scores, cautions
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.config import (  # noqa: E402
    EMBARGO_DAYS,
    HISTORY_PERIOD,
    HORIZON_DAYS,
    INDEX_TICKER,
    TRAINING_TICKERS,
)
from app.ml.data import PriceDataError, load_history  # noqa: E402
from app.ml.features import FEATURE_NAMES, chronological_split  # noqa: E402
from app.ml.trend import (  # noqa: E402
    TREND_TARGET_COLUMN,
    build_trend_training_table,
    evaluate_trend_probabilities,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("prepare_trend_dataset")

OUT_DIR = Path(__file__).resolve().parent.parent / "datasets"


def build_panel(period: str, refresh: bool) -> pd.DataFrame:
    """Concatenate per-ticker training tables into one panel."""
    try:
        index_px = load_history(INDEX_TICKER, period=period, refresh=refresh)
    except PriceDataError as exc:
        logger.error("Index history unavailable (%s); idx_* features cannot be built.", exc)
        raise SystemExit(1)

    frames, failed = [], []
    for ticker in TRAINING_TICKERS:
        try:
            px = load_history(ticker, period=period, refresh=refresh)
            table = build_trend_training_table(px, index_px, ticker=ticker)
            if table.empty:
                failed.append(ticker)
                continue
            frames.append(table)
            logger.info("  %-16s %5d rows  up-rate %.3f", ticker, len(table),
                        table[TREND_TARGET_COLUMN].mean())
        except (PriceDataError, ValueError) as exc:
            logger.warning("  %-16s FAILED: %s", ticker, exc)
            failed.append(ticker)

    if not frames:
        logger.error("No ticker produced usable rows. Aborting.")
        raise SystemExit(1)
    if failed:
        logger.warning("%d/%d tickers failed: %s", len(failed), len(TRAINING_TICKERS), failed)

    return pd.concat(frames).sort_index()


def write_report(panel: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> Path:
    """Plain-text summary, including the baseline a model has to beat."""
    train_rate = float(train[TREND_TARGET_COLUMN].mean())
    test_y = test[TREND_TARGET_COLUMN].to_numpy()

    # What "always predict the training base rate" scores on the test set
    baseline = evaluate_trend_probabilities(test_y, np.full(len(test_y), train_rate), train_rate)

    lines = [
        "Stock Trend Dataset Report",
        "=" * 44,
        "",
        f"Target             : {TREND_TARGET_COLUMN} (1 = closes higher in {HORIZON_DAYS} trading days)",
        f"Features           : {len(FEATURE_NAMES)} (shared with the volatility model)",
        f"Tickers            : {panel['ticker'].nunique()}",
        f"Rows (total)       : {len(panel):,}",
        f"Rows (train/test)  : {len(train):,} / {len(test):,}",
        f"Embargo            : {EMBARGO_DAYS} trading dates between splits",
        f"Date range         : {panel.index.min().date()} -> {panel.index.max().date()}",
        "",
        "Class balance",
        f"  train up-rate    : {train_rate:.4f}",
        f"  test  up-rate    : {float(test_y.mean()):.4f}",
        "",
        "THE BASELINE TO BEAT (constant prediction = train up-rate, scored on test)",
        f"  accuracy         : {baseline['baseline_accuracy']:.4f}   (always predicting the majority class)",
        f"  brier            : {baseline['baseline_brier']:.4f}",
        f"  log-loss         : {baseline['baseline_log_loss']:.4f}",
        "",
        "Rows per ticker",
    ]
    for ticker, count in panel["ticker"].value_counts().sort_index().items():
        lines.append(f"  {ticker:<16} {count:,}")

    lines += [
        "",
        "IMPORTANT",
        "-" * 44,
        "Accuracy alone is nearly meaningless here. If the up-rate is above",
        "0.5, a model that always says 'up' already scores that high. Judge",
        "a model on brier_skill_score from",
        "app.ml.trend.evaluate_trend_probabilities: positive means it beats",
        "the base rate, zero or negative means it does not. A model that",
        "does not beat it is a legitimate result worth reporting.",
        "",
        "Rows are NOT independent. Consecutive labels are overlapping 21-day",
        "windows, so the effective sample size is far below the row count.",
        "Split chronologically only; the provided files already apply the",
        "embargo.",
        "",
        "Do not add the forward return as a feature. It is excluded from the",
        "table on purpose because the label is derived from it.",
    ]

    path = OUT_DIR / "trend_report.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period", default=HISTORY_PERIOD)
    parser.add_argument("--refresh", action="store_true", help="ignore the price cache")
    parser.add_argument("--test-fraction", type=float, default=0.2)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    panel = build_panel(args.period, args.refresh)
    train, test = chronological_split(panel, test_fraction=args.test_fraction)

    panel.to_parquet(OUT_DIR / "trend_panel.parquet")
    train.to_parquet(OUT_DIR / "trend_train.parquet")
    test.to_parquet(OUT_DIR / "trend_test.parquet")
    report = write_report(panel, train, test)

    logger.info("")
    logger.info("Panel: %d rows x %d features, %s -> %s", len(panel), len(FEATURE_NAMES),
                panel.index.min().date(), panel.index.max().date())
    logger.info("Train/test: %d / %d", len(train), len(test))
    logger.info("Report: %s", report)


if __name__ == "__main__":
    main()
