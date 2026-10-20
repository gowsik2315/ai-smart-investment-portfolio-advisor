"""
Does the Stock Predictor's expected range actually contain the price?

A 68% band that only catches 55% of outcomes is worse than no band at
all: it looks like a measured statement and is not one. This backtests
the claim over every out-of-sample window in the training universe.

The comparison against trailing realised volatility matters too. If the
simple trailing estimate gave equally good intervals, the volatility
model would be earning nothing here.

Run from backend/:

    venv/Scripts/python.exe scripts/validate_expected_range.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

warnings.filterwarnings("ignore")

from app.ml.config import HORIZON_DAYS, INDEX_TICKER, TRADING_DAYS_PER_YEAR, TRAINING_TICKERS
from app.ml.data import load_history
from app.ml.features import FEATURE_NAMES, build_features
from app.ml.model_registry import load_model

Z68, Z95 = 1.0, 1.96
TEST_START = "2024-12-03"

artifact = load_model()
print(f"model: {artifact.model_version}")

index = load_history(INDEX_TICKER, period="10y")

rows = []
for ticker in TRAINING_TICKERS:
    try:
        hist = load_history(ticker, period="10y")
    except Exception as exc:
        print(f"  skip {ticker}: {exc}")
        continue

    feats = build_features(hist, index).dropna()
    feats = feats[feats.index >= TEST_START]
    if feats.empty:
        continue

    close = hist["close"].reindex(feats.index)
    fwd = hist["close"].shift(-HORIZON_DAYS).reindex(feats.index)
    ok = fwd.notna() & close.notna()
    feats, close, fwd = feats[ok], close[ok], fwd[ok]
    if feats.empty:
        continue

    sigma = np.array([artifact.predict(feats.iloc[[i]][FEATURE_NAMES])
                      for i in range(len(feats))], dtype=float)
    trailing = feats["rv_21"].to_numpy(dtype=float)

    spread = sigma * np.sqrt(HORIZON_DAYS / TRADING_DAYS_PER_YEAR)
    spread_hist = trailing * np.sqrt(HORIZON_DAYS / TRADING_DAYS_PER_YEAR)
    actual = np.log(fwd.to_numpy() / close.to_numpy())

    rows.append(pd.DataFrame({
        "ticker": ticker, "sigma": sigma, "trailing": trailing,
        "actual_log_return": actual, "spread": spread, "spread_hist": spread_hist,
    }))

data = pd.concat(rows, ignore_index=True)
print(f"scored {len(data):,} windows across {data.ticker.nunique()} tickers "
      f"(out of sample, from {TEST_START})\n")


def coverage(spread_col, z):
    s = data[spread_col].to_numpy()
    return float(np.mean(np.abs(data["actual_log_return"].to_numpy()) <= z * s)) * 100


print(f"{'band':<16}{'nominal':>9}{'MODEL sigma':>14}{'trailing rv_21':>16}")
print("-" * 58)
for label, z, nominal in [("68% (likely)", Z68, 68.3), ("95% (wide)", Z95, 95.0)]:
    print(f"{label:<16}{nominal:>8.1f}%{coverage('spread', z):>13.1f}%"
          f"{coverage('spread_hist', z):>15.1f}%")

print()
print("Sigma distribution (annualised):")
realised = data["actual_log_return"].abs() * np.sqrt(TRADING_DAYS_PER_YEAR / HORIZON_DAYS)
for name, series in [("model forecast", data["sigma"]), ("trailing rv_21", data["trailing"])]:
    print(f"  {name:<16} mean {series.mean():.3f}  p5 {series.quantile(0.05):.3f}  "
          f"p95 {series.quantile(0.95):.3f}")

# What single multiplier would fix the 68% band?
abs_ret = data["actual_log_return"].abs().to_numpy()
spread = data["spread"].to_numpy()
needed = np.percentile(abs_ret / spread, 68.3)
print(f"\nMultiplier that would make the 68% band hit 68.3%: {needed:.3f}")
needed95 = np.percentile(abs_ret / spread, 95.0)
print(f"Multiplier that would make the 95% band hit 95.0%: {needed95 / Z95:.3f}")

# Aggregate coverage can hide a conditional failure: compression makes the
# band too wide when calm and too narrow when stressed, which can average
# out to "fine" while being wrong exactly when it matters.
print("\nConditional coverage, by quintile of TRAILING volatility (the regime):")
data["regime"] = pd.qcut(data["trailing"], 5, labels=["calmest", "calm", "mid", "stressed", "most stressed"])
print(f"{'regime':<16}{'n':>7}{'68% band':>11}{'95% band':>11}{'mean sigma':>12}{'mean |ret| ann':>16}")
print("-" * 76)
for name, grp in data.groupby("regime", observed=True):
    s = grp["spread"].to_numpy(); a = np.abs(grp["actual_log_return"].to_numpy())
    c68 = np.mean(a <= Z68 * s) * 100
    c95 = np.mean(a <= Z95 * s) * 100
    ann = (grp["actual_log_return"].abs() * np.sqrt(TRADING_DAYS_PER_YEAR / HORIZON_DAYS)).mean()
    print(f"{name:<16}{len(grp):>7,}{c68:>10.1f}%{c95:>10.1f}%{grp['sigma'].mean():>12.3f}{ann:>16.3f}")
