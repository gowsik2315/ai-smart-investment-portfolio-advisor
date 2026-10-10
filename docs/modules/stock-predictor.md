# Stock Predictor

A 21-trading-day outlook for one stock: where it is trending now, the
probability it closes higher, and how far it may plausibly move.

Page: `/stock-predictor` · API: `GET /api/ml/trend-outlook/{ticker}`

---

## What it does and does not claim

It does **not** predict a price. Daily prices are close to a random walk, and a
price target would imply precision that does not exist.

It reports three separate things, each labelled for what it is:

| Output | What it is | Is it a forecast? |
|---|---|---|
| **Current trend** | Bullish / Neutral / Bearish from four technical signals | No. It describes the past |
| **Probability of a rise** | Chance the stock closes higher 21 trading days from now | Only when `probability_source` is `ml_predicted` |
| **Expected range** | 68% and 95% price bands out to day 21 | A spread, with no direction |

The range is centred on today's price. It says how far the stock may move, not
which way. Direction lives only in the probability.

## The baseline matters more than the model

Over a month, large-cap stocks rise more often than they fall, so a model that
always says "up" is right more than half the time. Accuracy alone is therefore
close to meaningless, and a probability of 55% means little until it is compared
with what the stock does anyway.

The response always carries `base_rate_up`, the stock's own historical share of
21-day windows that ended higher, and the page always shows it beside the
probability. A trained model is only worth shipping if it beats that baseline on a
proper scoring rule. `evaluate_trend_probabilities` reports the **Brier skill
score**: positive means the model beats the base rate; zero or negative means it
does not.

The dataset built for this module shows why this is not a formality. With the 10
NSE tickers and ten years of history, the training period rose in **58.3%** of
windows but the test period only **45.6%**. A model, or a constant predictor,
fitted on the training period is therefore biased towards "up" and scores below a
coin flip on the test period. The market regime shifted between train and test.

## Fallback chain

```
probability:   trained classifier  ->  the stock's own historical base rate
                 'ml_predicted'            'historical_base_rate'
```

No model is shipped. Until one is trained and saved, the probability **is** the
base rate, and the page says so in an amber "Not a prediction" banner, so a
statistic is never presented as machine learning. The service always returns an
outlook when price history exists. Only missing or too-short history is an error.

A model is also bypassed, with the reason recorded in `fallback_reason`, if it
returns NaN or a value outside [0, 1], raises, or the history is too short to build
its features.

## API

All endpoints require a bearer token.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/ml/trend-outlook/{ticker}` | The outlook described below |
| GET | `/api/market/stock/{ticker}/outlook/explain` | AI-written explanation of it (see below) |
| GET | `/api/ml/trend-model-info` | Whether a classifier is loaded, plus its metrics |
| POST | `/api/ml/reload-trend-model` | Re-read the artifact after training |

Errors: `422` for a malformed ticker, `503` when no price data can be obtained,
`400` when history is too short (fewer than 126 trading days).

### Response (abridged)

```json
{
  "ticker": "RELIANCE.NS",
  "as_of": "2026-10-09",
  "last_close": 1173.2,
  "horizon_days": 21,
  "probability_up": 0.4951,
  "probability_source": "historical_base_rate",
  "base_rate_up": 0.4951,
  "fallback_reason": "No trend model artifact at ...",
  "model_version": null,
  "model_metrics": null,
  "trend": {"label": "Bearish", "score": -1.0, "signals": [...], "rsi_14": 38.7, "rsi_state": "neutral"},
  "volatility": 0.2248,
  "volatility_source": "historical_fallback",
  "expected_range": [{"day": 0, "median": 1173.2, "lower_68": 1173.2, "...": "..."}],
  "recent_prices": [{"date": "2026-04-10", "close": 1380.1}],
  "disclaimer": "..."
}
```

The range's volatility comes from the existing volatility service, so it is an ML
forecast when that model is trained and trailing realised volatility otherwise,
and `volatility_source` says which.

## The four trend signals

Each is bullish or bearish; the score is the net share and the label thresholds
are +-0.5. A signal that needs more history than exists is omitted, not guessed.

1. Price above its 50-day average
2. 50-day average above the 200-day average
3. 1-month (21-day) momentum positive
4. 3-month (63-day) momentum positive

RSI is shown for information only and is not part of the score.

## AI explanation

An optional **Explain** button on the page asks the local LLM (Ollama) to
describe the outlook in plain language. It is clearly labelled as AI-written and
is kept off `/api/ml/*` on purpose, so the distinction between a model output and
generated prose survives in the API:

`GET /api/market/stock/{ticker}/outlook/explain`

It is a button and not automatic because the 3B model needs roughly 30-60s per
answer on CPU. Successful explanations are cached in memory for six hours, keyed
on everything the prompt uses, so reopening a stock is instant and a changed
number never gets a stale explanation. Failures and discarded texts are never
cached. If Ollama is down the page degrades quietly and the numbers stand alone.

### Why there is an output guard

The prompt forbids advice and certainty and, for a base-rate probability, requires
the text to say it is not a prediction. A small model follows that loosely, and in
a finance context "loosely" is not enough. Tested against the real model, it wrote
"the stock *will* close higher" and, separately, left out the plain statement that
no model is loaded. So `app/services/explanation_guard.py` checks the text after
generation:

- **Rejected** (discarded, never edited): buy/sell/hold advice, guarantees, and
  price moves stated as certain. A rejected text is reported as such and the user
  can regenerate.
- **Appended**: when the probability is only the base rate and the text does not
  already say it is not a prediction, a fixed sentence saying so is added.
- **Not flagged**: a *denied* assurance. "Does not guarantee future performance"
  is the disclaimer we want, and an early version of the guard wrongly rejected it.

The prompt also supplies the exact sentence to use for the probability, because a
small model copies a template far more reliably than it obeys a prohibition.

## Training the model

The plumbing is complete and the model is left for you to train, as with the
volatility model.

```bash
cd backend
python -m ml.prepare_trend_dataset
```

This writes `datasets/trend_{panel,train,test}.parquet` and
`trend_report.txt`, which states the baseline scores to beat. Then:

```python
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from app.ml.features import FEATURE_NAMES
from app.ml.trend import TREND_TARGET_COLUMN, evaluate_trend_probabilities
from app.ml.trend_registry import save_trend_model

train = pd.read_parquet("datasets/trend_train.parquet")
test = pd.read_parquet("datasets/trend_test.parquet")

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
model.fit(train[FEATURE_NAMES], train[TREND_TARGET_COLUMN].astype(int))

p_up = model.predict_proba(test[FEATURE_NAMES])[:, 1]
metrics = evaluate_trend_probabilities(
    test[TREND_TARGET_COLUMN], p_up, train[TREND_TARGET_COLUMN].mean())
print(metrics)            # check brier_skill_score before saving

save_trend_model(model, "logreg-v1", metrics=metrics)
```

Then `POST /api/ml/reload-trend-model`. The page switches to a green "Model
prediction" banner and shows the held-out metrics next to the forecast. If the
Brier skill score is zero or negative the banner says the model did not beat the
base rate. That is a legitimate result, and worth reporting as one.

### Rules that keep the result honest

- **Features are shared** with the volatility model (`app.ml.features`), so
  training and inference cannot drift apart.
- **The label is defined once**: `TARGET_UP_COLUMN` in `app/ml/config.py` and
  `build_target_up` in `app/ml/features.py`, aligned row-for-row with the
  volatility target. `trend.py` reuses both rather than keeping its own copy.
- **The forward return is not in the training table.** The label is derived from
  it, so leaving it in would feed the model its own answer.
- **Split chronologically** with the 21-date embargo. Consecutive labels overlap
  by 20 of 21 days, so a random split leaks.
- **Rows are not independent.** Treat confidence in any metric accordingly.
- **Judge on Brier skill, not accuracy.**
- **The artifact contract is enforced at load.** Feature order and horizon must
  match, and a volatility artifact is refused as a trend model. A mismatched
  model is rejected, never served.

## Files

| File | Role |
|---|---|
| `backend/app/ml/trend.py` | Target, trend signals, base rate, expected range, scoring |
| `backend/app/ml/trend_registry.py` | Classifier artifact: save, load, contract checks |
| `backend/app/services/stock_trend_service.py` | Assembles the outlook; owns the fallback chain |
| `backend/app/api/ml.py` | The three `/api/ml` endpoints |
| `backend/app/api/market.py` | The AI explanation endpoint |
| `backend/app/services/explanation_guard.py` | Checks the LLM output against the wording rules |
| `backend/app/services/ollama_prompts.py` | `stock_outlook_explanation`, the prompt |
| `backend/ml/prepare_trend_dataset.py` | Builds the training panel and baseline report |
| `backend/tests/test_ml_trend.py` | 69 tests |
| `backend/tests/test_ml_explain.py` | 53 tests: prompt rules, guard, endpoint |
| `frontend/src/pages/StockPredictor.js` | The page |

## Limitations

- Direction over one month is close to unpredictable. The honest expectation is a
  small or zero edge over the base rate.
- Trained on ten large NSE stocks. Other markets reuse the Nifty 50 as market
  context and are less reliable.
- The range assumes returns are normally distributed with the volatility held
  constant. Real returns have fatter tails, so the 95% band is optimistic in a
  crash.
- `yfinance` is an unofficial scraper and can rate-limit or break; history is
  cached to disk.
- `POST /reload-trend-model` is open to any authenticated user and needs an admin
  role before deployment.
- The AI explanation is only as reliable as a 3B model. The guard stops advice and
  certainty, but it cannot verify that every sentence is faithful to the numbers.
- Educational analysis, not investment advice.
