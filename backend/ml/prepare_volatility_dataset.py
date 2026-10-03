"""
Build the volatility-forecasting training dataset.

Downloads price history for the training universe, builds features and
the 21-day forward realised-volatility target, and writes a single panel
to disk ready for model fitting.

This script deliberately stops short of training. Choosing and fitting
the model is a separate step; what this guarantees is that whatever you
fit is fitted on features built by the same code the API uses at
inference time (`app.ml.features.build_features`).

Usage
-----
    cd backend
    venv/Scripts/python.exe -m ml.prepare_volatility_dataset
    venv/Scripts/python.exe -m ml.prepare_volatility_dataset --refresh
    venv/Scripts/python.exe -m ml.prepare_volatility_dataset --period 5y

Outputs (under backend/datasets/)
---------------------------------
    volatility_panel.parquet   features + target + ticker, all tickers
    volatility_train.parquet   chronological training split
    volatility_test.parquet    held-out test split, after the embargo
    volatility_report.txt      row counts, date ranges, target summary
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.config import (  # noqa: E402
    EMBARGO_DAYS,
    HISTORY_PERIOD,
    HORIZON_DAYS,
    INDEX_TICKER,
    TARGET_COLUMN,
    TRAINING_TICKERS,
)
from app.ml.data import PriceDataError, load_history  # noqa: E402
from app.ml.features import (  # noqa: E402
    FEATURE_NAMES,
    build_training_table,
    chronological_split,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("prepare_volatility_dataset")

OUT_DIR = Path(__file__).resolve().parent.parent / "datasets"


def build_panel(period: str, refresh: bool) -> pd.DataFrame:
    """Concatenate per-ticker training tables into one panel."""
    logger.info("Loading index %s", INDEX_TICKER)
    try:
        index_px = load_history(INDEX_TICKER, period=period, refresh=refresh)
    except PriceDataError as exc:
        logger.error(
            "Index history unavailable (%s). The idx_* features cannot be "
            "built, and every row would be dropped. Aborting.", exc,
        )
        raise SystemExit(1)

    frames, failed = [], []

    for ticker in TRAINING_TICKERS:
        try:
            px = load_history(ticker, period=period, refresh=refresh)
            table = build_training_table(px, index_px, ticker=ticker)
            if table.empty:
                failed.append((ticker, "no complete rows"))
                continue
            frames.append(table)
            logger.info(
                "  %-16s %5d rows  %s -> %s",
                ticker, len(table), table.index.min().date(), table.index.max().date(),
            )
        except (PriceDataError, ValueError) as exc:
            logger.warning("  %-16s FAILED: %s", ticker, exc)
            failed.append((ticker, str(exc)))

    if not frames:
        logger.error("No ticker produced usable rows. Aborting.")
        raise SystemExit(1)

    if failed:
        logger.warning("%d/%d tickers failed: %s",
                       len(failed), len(TRAINING_TICKERS), [t for t, _ in failed])

    return pd.concat(frames).sort_index()


def write_report(panel: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> Path:
    """Write a plain-text summary of the dataset."""
    target = panel[TARGET_COLUMN]
    lines = [
        "Volatility Forecasting Dataset Report",
        "=" * 44,
        "",
        f"Target             : {TARGET_COLUMN}",
        f"Horizon            : {HORIZON_DAYS} trading days, annualised",
        f"Features           : {len(FEATURE_NAMES)}",
        f"Tickers            : {panel['ticker'].nunique()}",
        f"Rows (total)       : {len(panel):,}",
        f"Rows (train/test)  : {len(train):,} / {len(test):,}",
        f"Embargo            : {EMBARGO_DAYS} trading dates between splits",
        f"Date range         : {panel.index.min().date()} -> {panel.index.max().date()}",
        "",
        "Target distribution (annualised volatility)",
        f"  mean   {target.mean():.4f}",
        f"  std    {target.std():.4f}",
        f"  min    {target.min():.4f}",
        f"  p25    {target.quantile(0.25):.4f}",
        f"  median {target.median():.4f}",
        f"  p75    {target.quantile(0.75):.4f}",
        f"  max    {target.max():.4f}",
        "",
        "Rows per ticker",
    ]
    for ticker, count in panel["ticker"].value_counts().sort_index().items():
        lines.append(f"  {ticker:<16} {count:,}")

    lines += [
        "",
        "Missing values: " + ("none" if not panel.isna().any().any() else "PRESENT - investigate"),
        "",
        "IMPORTANT",
        "-" * 44,
        "Rows are NOT independent. Consecutive targets are overlapping",
        "21-day windows, so the effective sample size is far below the row",
        "count. Confidence intervals computed as if rows were independent",
        "will be too narrow.",
        "",
        "Split chronologically only. The provided train/test files already",
        "apply the embargo; if you re-split, use",
        "app.ml.features.chronological_split rather than a random split.",
        "",
        "Beat the baselines before shipping: naive persistence (rv_21),",
        "HAR, and GARCH(1,1). See app/ml/evaluation.py and app/ml/README.md.",
    ]

    path = OUT_DIR / "volatility_report.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period", default=HISTORY_PERIOD,
                        help=f"yfinance period string (default: {HISTORY_PERIOD})")
    parser.add_argument("--refresh", action="store_true",
                        help="ignore the price cache and re-download")
    parser.add_argument("--test-fraction", type=float, default=0.2,
                        help="share of rows held out at the end (default: 0.2)")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    panel = build_panel(args.period, args.refresh)
    train, test = chronological_split(panel, test_fraction=args.test_fraction)

    panel.to_parquet(OUT_DIR / "volatility_panel.parquet")
    train.to_parquet(OUT_DIR / "volatility_train.parquet")
    test.to_parquet(OUT_DIR / "volatility_test.parquet")
    report = write_report(panel, train, test)

    logger.info("")
    logger.info("Wrote:")
    for name in ["volatility_panel.parquet", "volatility_train.parquet",
                 "volatility_test.parquet", "volatility_report.txt"]:
        logger.info("  %s", OUT_DIR / name)
    logger.info("")
    logger.info("Panel: %d rows x %d features, %s -> %s",
                len(panel), len(FEATURE_NAMES),
                panel.index.min().date(), panel.index.max().date())
    logger.info("Train/test: %d / %d", len(train), len(test))
    logger.info("Report: %s", report.name)


if __name__ == "__main__":
    main()
