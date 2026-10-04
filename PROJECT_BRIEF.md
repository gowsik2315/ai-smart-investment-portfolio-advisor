# Project Brief

A self-contained summary for consulting an AI assistant that has no
access to this repository. Paste the whole file into the conversation.

---

## What the project is

A web application that helps an individual investor in India plan a
portfolio. The user enters their financial details; the app works out
their risk profile, suggests an asset allocation, analyses a portfolio's
risk and diversification, projects future value with Monte Carlo
simulation, plans SIP (monthly) investments, and looks up stock data.
Every analysis screen can also produce a plain-English explanation from
a local LLM.

Built as a personal/academic project, not deployed.

## Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy, SQLite, Alembic
- **Frontend:** React 18 (Create React App), Tailwind, Recharts
- **LLM:** Ollama running `qwen2.5:3b` locally (CPU, ~10 tokens/sec)
- **Market data:** Yahoo Finance via `yfinance` — no API key needed
- **ML:** scikit-learn, with `arch`/`statsmodels` for baselines
- 54 API operations, 14 frontend pages, 118 passing tests

## The nine modules

| Module | What it does | How |
|---|---|---|
| Auth | Register / login | JWT + bcrypt |
| Financial Profile | Age, income, savings, horizon, goal | Stored per user |
| Risk Assessment | Score 0-100 → Conservative / Moderate / Aggressive | **Rule-based** weighted formula |
| Portfolio Recommendation | Allocation across stocks / funds / gold / emergency | **Rule-based** templates by risk score |
| Portfolio Analytics | Volatility, Sharpe ratio, max drawdown | Computed from a value series |
| Diversification Analysis | Concentration score, warnings | HHI + **sector labels supplied by the caller** |
| Monte Carlo | 10,000 simulated 10-year paths, VaR/CVaR | Geometric Brownian motion |
| SIP Planner | Monthly investment projections | Compound interest formula |
| Stock Explorer | Price, history, company info | yfinance |

## Two separate AI/ML features — do not conflate them

1. **AI-generated explanation** — the local LLM turns computed numbers
   into prose. Present on 7 endpoints. Produces text, predicts nothing.
2. **ML-based volatility forecasting** — a trained regressor that
   predicts the volatility (sigma) that Monte Carlo needs. Produces a
   number, no text.

## Current state

**Working:** all nine modules, end to end, frontend and backend. Auth
enforced on every data endpoint, per-user data scoping, 118 tests,
Alembic migrations, pushed to a private GitHub repo.

**Not done — the single open item:**
The volatility model is **not trained yet**. The entire integration path
exists and is tested: a shared feature pipeline (21 features from price
history), a saved-model contract, an API endpoint, and a fallback. Until
a model is saved, the app returns *trailing historical volatility* and
labels it `historical_fallback` so it is never passed off as a
prediction. Everything still works; it just isn't ML yet.

**Also outstanding:** SQLite → PostgreSQL, real deployment (AWS),
`SECRET_KEY` is still a placeholder.

## The ML work, as decided so far

- **Target:** realised volatility over the next 21 trading days,
  annualised. Deliberately *not* predicting returns — returns are close
  to unpredictable from price history, whereas volatility persists.
- **Data:** 10 liquid NSE large caps plus the Nifty index (`^NSEI`),
  ~5 years of daily bars. A ready-to-train panel of 9,680 rows × 21
  features already exists on disk, split chronologically with a 21-day
  embargo so overlapping targets cannot leak between train and test.
- **Must beat these baselines**, scored on RMSE, MAE and QLIKE:
  naive persistence ("next month equals this month"), HAR, GARCH(1,1).
  If it loses to them, that is a legitimate result worth reporting.
- **Deliberately rule-based, not ML:** Risk Assessment and Portfolio
  Recommendation. There is no real-world label for "correct investor
  type" or "correct allocation", so a model would just relearn the rule
  used to invent its training labels. A 50,000-row synthetic investor
  dataset in the repo demonstrates this trap and is unused by the app.

## Open questions to decide

1. **Which model to train** for volatility — Ridge/HAR-style linear,
   Random Forest, gradient boosting — and whether it beats the baselines.
2. **Whether to add any further ML.** Three candidates discussed:
   - *Covariance / correlation estimation* — measure diversification
     from how holdings actually move together, rather than from sector
     labels. Would also enable multi-asset Monte Carlo and mean-variance
     optimisation. Highest value, because it fixes something currently
     measured wrongly.
   - *Market regime detection* — unsupervised (Gaussian Mixture / HMM)
     identification of calm vs stressed markets, to condition
     projections and explanations.
   - *Drawdown forecasting* — predict the worst peak-to-trough fall over
     the horizon, reusing the volatility pipeline.
3. **Scope vs deadline**, given CPU-only hardware (no GPU).

## Constraints worth knowing

- CPU only, no GPU. Training must be cheap; the LLM is already slow
  (90-120s per explanation, cached afterwards).
- `yfinance` is an unofficial scraper: rate-limited, can break, not
  licensed for commercial use. Price history is cached to disk.
- Monte Carlo assumes constant return and volatility over the horizon,
  a single portfolio-level sigma, and no correlation between holdings.
- Terminal values are lognormal, so the **median** is the trustworthy
  "typical outcome", not the mean.
