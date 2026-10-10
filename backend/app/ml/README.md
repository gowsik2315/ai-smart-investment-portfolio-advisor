# ML-Based Volatility Forecasting — Integration Contract

Everything the application needs in order to consume a volatility
forecast is already built and wired. What remains is training a model
and saving it. This document is the contract between the two.

Two labels are kept deliberately distinct throughout the codebase and
should stay distinct in any write-up:

| Label | What it is | Where it lives |
|---|---|---|
| **ML-based volatility forecasting** | A trained regressor predicting 21-day forward realised volatility | `app/ml/`, `app/services/ml_prediction_service.py`, `/api/ml/*` |
| **AI-generated explanation** | Ollama / `qwen2.5:3b` turning numbers into prose | `app/services/ollama_service.py`, `/api/*/explain` |

They are different features. The LLM does no forecasting, and the
forecasting model produces no text.

---

## What is predicted, and why that choice

**Target:** realised volatility of daily log returns over the **next 21
trading days**, annualised by `sqrt(252)`.

Not returns. Daily and monthly stock returns are close to unpredictable
from price and volume history; a return model will score near zero or
negative R-squared out of sample. That is a legitimate finding but a
weak foundation for a product feature. Volatility clusters and persists,
so a model can beat a naive baseline by a margin you can measure and
defend — and sigma is exactly the input Monte Carlo needs.

The expected return fed to Monte Carlo stays a historical or
user-supplied assumption. Only sigma comes from the model.

---

## The contract

### 1. Build features with `build_features`

```python
from app.ml.data import load_history
from app.ml.features import build_training_table
from app.ml.config import TRAINING_TICKERS, INDEX_TICKER, TARGET_COLUMN

index = load_history(INDEX_TICKER)
panel = pd.concat([
    build_training_table(load_history(t), index, ticker=t)
    for t in TRAINING_TICKERS
])
```

Do **not** hand-roll features in the notebook. `app.ml.features` is
imported by the live prediction service; if training computes features
any other way, the served model receives inputs it never saw during
fitting. That failure is silent — predictions come back plausible and
wrong — which is why the artifact records its feature list and the loader
refuses to serve on a mismatch.

The table holds the 21 features plus **two labels**: `TARGET_COLUMN`
(`target_rv_21d`, next-21-day realised volatility, for the volatility
model) and `TARGET_UP_COLUMN` (`target_up_21d`, 1 if the close 21 trading
days ahead is above today's, else 0, for the trend classifier). Both look
ahead with the same `HORIZON_DAYS` and `shift(-HORIZON_DAYS)`, so they are
undefined on exactly the same final rows and joining them costs no rows.

**Neither label is a feature.** Select model inputs with
`table[FEATURE_NAMES]`, never by dropping your own target and keeping the
rest: the other label is a future quantity, and a model fitted on it looks
excellent offline and is worthless live. A trend classifier that should not
even carry the volatility label in its table can use
`app.ml.trend.build_trend_training_table`.

The 21 features are listed in `features.FEATURE_NAMES`: lagged returns,
realised volatility at 5/10/21/63 days, the 5-to-21 and 21-to-63
volatility ratios, Parkinson and Garman-Klass range estimators,
volume relative to its 20-day mean, 21- and 63-day momentum, RSI(14),
drawdown from the 52-week high, and index volatility and momentum.

### 2. Split chronologically, with the embargo

```python
from app.ml.features import chronological_split
train, test = chronological_split(panel.sort_index(), test_fraction=0.2)
```

Never shuffle. And note the embargo: consecutive 21-day targets overlap,
so the target on the last training row is built from returns that extend
21 days into the test period. Splitting without a gap lets the model see
part of its own test window during fitting and inflates every metric.
`chronological_split` drops `EMBARGO_DAYS` rows between the two halves.

For walk-forward validation inside the training half, use
`sklearn.model_selection.TimeSeriesSplit` — and keep the same embargo in
mind there too.

### 3. Beat the baselines, and report them

```python
from app.ml.evaluation import (
    naive_persistence, fit_har, predict_har,
    garch_forecast_series, compare_forecasts,
)

har = fit_har(train, TARGET_COLUMN)

table = compare_forecasts(
    actual=test[TARGET_COLUMN],
    forecasts={
        "naive_persistence": naive_persistence(test),
        "har":               predict_har(har, test),
        "your_model":        pd.Series(model.predict(test[FEATURE_NAMES]), index=test.index),
    },
)
print(table)   # rmse / mae / qlike / r2 + improvement vs baseline
```

Three baselines matter:

- **Naive persistence** — "next month's volatility equals this month's".
  Volatility is persistent enough that this is already a decent forecast.
  A model that does not beat it has not earned a place in the product.
- **HAR** — linear regression on 5/21/63-day realised volatility. A
  famously strong baseline, frequently competitive with far more complex
  models. Include it; omitting it is the easiest way to make a weak
  model look good.
- **GARCH(1,1)** — via `arch`. `garch_forecast_series` does walk-forward
  fits with a configurable refit cadence. Slow; budget for it.

Report **RMSE, MAE and QLIKE** against all three. QLIKE is the standard
asymmetric loss for volatility: it penalises under-forecasting risk much
harder than over-forecasting it, which is the correct asymmetry for a
risk tool. `app.ml.evaluation.qlike` implements the zero-anchored form,
computed on variances.

If the model loses to the baselines, say so. That is a publishable
result and a much better outcome than shipping a forecast that is worse
than "same as last month" while labelled as machine learning.

### 4. Save through `save_model`

```python
from app.ml.model_registry import save_model

save_model(
    model=fitted_estimator,
    model_version="ridge-har-v1",
    metrics={"rmse": 0.081, "mae": 0.058, "qlike": 0.214,
             "baseline_rmse": 0.094, "baseline_qlike": 0.238},
    notes="Ridge on 21 features. Beats naive persistence by 14% RMSE, 10% QLIKE.",
)
```

This writes `backend/models/volatility_model.joblib` containing the
estimator **plus** its feature list, horizon, training timestamp and
metrics. A bare `joblib.dump` is rejected at load time.

Any object with a `.predict(DataFrame)` method works — scikit-learn
estimators, a `Pipeline`, or your own wrapper. If you trained on a
subset of the features, pass `feature_names=[...]` explicitly.

### 5. Pick it up without restarting

```
POST /api/ml/reload-model
```

---

## How the app consumes the forecast

```
POST /api/ml/predict-volatility   {"ticker": "RELIANCE.NS"}
GET  /api/ml/model-info           is a model loaded, and which
GET  /api/ml/features/{ticker}    the exact inputs a prediction would use
GET  /api/ml/cache-status          price cache + available artifacts
```

And in Monte Carlo:

```json
POST /api/monte-carlo/simulate
{
  "initial_investment": 100000,
  "expected_return": 0.12,
  "use_predicted_volatility": true,
  "ticker": "RELIANCE.NS",
  "years": 10,
  "random_seed": 42
}
```

### The fallback chain

The service never leaves a caller without a usable sigma:

1. **ML forecast** from the saved artifact → `source: "ml_predicted"`
2. **Trailing 21-day realised volatility** → `source: "historical_fallback"`
3. **Hard failure** only when no price history can be obtained at all

Every response carries `volatility_provenance`, so the UI can state
where the number came from. Trailing realised volatility must never be
presented as a prediction — note that it is also precisely the
naive-persistence baseline, so if the model cannot beat it offline, the
"fallback" is not a degradation at all.

The ML path is abandoned in favour of the fallback when: no artifact
exists, the artifact's features disagree with the running code, history
is too short for a complete feature row, `.predict()` raises, or the
output is non-finite or outside
`[MIN_PLAUSIBLE_VOLATILITY, MAX_PLAUSIBLE_VOLATILITY]` (1%–300%
annualised). That last guard matters: a regressor can emit a negative
number, and feeding it to Monte Carlo would produce confident nonsense
rather than an error.

---

## Things already handled

- **The volatility cap was 1.0.** A model-predicted sigma above 100%
  annualised — entirely possible for a single NSE equity in a crisis
  window — would have been rejected with a 422 before reaching the
  simulator. The cap is now 5.0 as a sanity ceiling.
- **The simulator was additive.** `S * (1 + r)` with normal `r` can
  drive a path negative once sigma is large, which was survivable with a
  hand-typed 15% and not survivable with a predicted 80%. It is now
  geometric (log-space steps with the Ito correction), so paths stay
  positive and the arithmetic mean still matches the requested
  `expected_return`.
- **`random_seed`** is plumbed through. Use a fixed seed when comparing
  predicted sigma against manual sigma, so the difference you see is the
  parameter and not the draw.
- **Mean vs median.** Terminal values are lognormal. At high sigma the
  sample mean is dominated by a few enormous paths and badly overstates
  the typical outcome — at sigma = 120% the sample mean of 50,000 paths
  sits ~47% below the analytic mean. The explanation prompt now leads
  with the median. Prefer `scenarios.average_case` over
  `statistics.mean_value` anywhere a "typical" outcome is shown.

---

## Caveats worth stating in the write-up

- **The universe is 10 large caps.** Conclusions do not automatically
  extend to mid or small caps, where liquidity and volatility dynamics
  differ.
- **Rows are not independent.** Overlapping 21-day targets mean the
  effective sample size is far below the row count. Confidence intervals
  computed as if rows were independent will be too narrow.
- **One market, one regime mix.** Ten years of NSE data covers a limited
  number of volatility regimes. Out-of-sample here is not the same as
  out-of-regime.
- **`yfinance` is an unofficial scraper.** Data can be revised, gapped,
  or rate-limited. History is cached to `backend/data_cache/` for this
  reason; `load_history` will serve a stale cache rather than fail.

## Stock trend outlook (the second model)

The same feature pipeline also feeds the Stock Predictor, which estimates
the probability a stock closes higher in 21 trading days. Only the target and
the artifact differ.

| | Volatility model | Trend model |
|---|---|---|
| Target | next-21-day realised volatility (regression) | closes higher in 21 days (0/1 classification) |
| Target code | `features.build_target` | `trend.build_trend_target` |
| Artifact | `VolatilityModelArtifact` via `save_model` | `TrendModelArtifact` via `save_trend_model` |
| File | `models/volatility_model.joblib` | `models/trend_model.joblib` |
| Must beat | naive persistence, HAR, GARCH(1,1) | the stock's own historical base rate |
| Score with | RMSE / MAE / QLIKE | Brier skill score (`trend.evaluate_trend_probabilities`) |

Two rules are specific to the trend model:

- **Judge on Brier skill, not accuracy.** Large stocks rise more often than
  they fall over a month, so "always up" already scores above 50%. On the
  shipped dataset the train period rose in 58% of windows but the test
  period only 46%, so a base-rate predictor scores below a coin flip
  out-of-sample.
- **The forward return is not in the training table.** The label is derived
  from it; leaving it in would feed the model its own answer.

Build the data with `python -m ml.prepare_trend_dataset`. The full guide,
including a worked training example, is
[`docs/modules/stock-predictor.md`](../../../docs/modules/stock-predictor.md).
