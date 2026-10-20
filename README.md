# 🎯 AI Smart Investment Portfolio Advisor

> An intelligent investment portfolio management system powered by AI, providing personalized recommendations, risk analysis, and portfolio optimization.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-406%20passing-brightgreen.svg)](backend/tests/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 About

The **AI Smart Investment Portfolio Advisor** is a comprehensive financial management platform that combines:

- 🤖 **AI-generated explanations** using Ollama (local LLM, `qwen2.5:3b`)
- 📉 **ML-based volatility forecasting** feeding Monte Carlo's sigma
- 📊 **Advanced Analytics** with Monte Carlo simulations (geometric Brownian motion)
- 💹 **Market Data** via Yahoo Finance (`yfinance`, no API key required)
- 📈 **Portfolio Optimization** with risk-adjusted strategies
- 🎯 **Goal-Based Planning** for retirement, education, wealth creation

---

## ✨ Key Features

### 🔐 User Management
- Secure registration and authentication
- JWT-based session management
- Profile and preferences management

### 💰 Financial Profile
- Income and expense tracking
- Savings rate analysis
- Investment goals definition
- Time horizon planning

### 📊 Risk Assessment
- Automated risk profiling
- AI-powered risk tolerance analysis
- Personalized risk scores
- Historical risk tracking

### 🎯 Portfolio Recommendation
- AI-generated asset allocation
- Custom portfolio strategies (Conservative, Moderate, Aggressive)
- Sector-wise distribution
- Rebalancing suggestions

### 💼 Portfolio Tracking
- Record buys, sells, SIP instalments and dividends against named portfolios
- Holdings, cost basis and P&L are **derived from the transaction ledger**
  (average-cost accounting), never stored, so they cannot drift out of step
- Live valuation from yfinance; a holding that cannot be priced falls back to
  its last transaction price and is **labelled** `last_transaction_price`
- Realised vs unrealised profit, dividend income, per-holding weights
- A sale larger than the quantity held on that date is rejected, so the stored
  history can never describe an impossible position
- Feeds real holdings into Diversification Analysis

### 📈 Portfolio Analytics
- **Runs on your real holdings**: the daily value series is rebuilt from your
  transaction ledger and historical prices
- Analyses all portfolios combined by default, or one in isolation, so two
  strategies can be compared
- Charted as an index rebased to 100, never in rupees: cashflows are excluded,
  so its level is not your balance and must not be read as one
- **Time-weighted**, so deposits and withdrawals are not mistaken for returns —
  the convention funds use to report performance independently of cashflows
- Annualised volatility, Sharpe ratio, maximum drawdown, composite risk score
- Holdings with no price history are excluded and reported, because carrying
  them at a flat value would understate volatility
- Sample data still available, explicitly labelled as not your portfolio

### 🌈 Diversification Analysis
- **Runs on your real holdings** from Portfolio Tracking, valued at current prices
- Analyses all portfolios combined by default, or one in isolation
- Sectors resolved automatically from market data (no manual tagging)
- Reports what share of the portfolio by value could actually be classified,
  so a score built on unknown sectors is never passed off as a verdict
- Sector diversification scoring, asset class distribution, HHI
- Concentration risk identification and recommendations
- Sample data still available, explicitly labelled as not your portfolio

### 🎲 Monte Carlo Simulation
- 10,000+ simulation runs
- Probability distribution analysis
- Best/worst/average case scenarios
- Confidence interval projections

### 💵 SIP Calculator
- Systematic Investment Plan projections
- Year-wise growth visualization
- Goal-based SIP planning
- Wealth creation estimates

### 📉 Stock Explorer
- Real-time stock price data
- Historical price charts
- Company information
- AI-powered trend analysis

### 🤖 AI-Generated Explanations
- Natural language investment insights via a local LLM (`qwen2.5:3b`)
- Plain-English readings of risk profiles, allocations and simulations
- Cached per record, so an explanation is generated once
- Degrades gracefully: the app stays fully usable with Ollama offline

### 📉 ML-Based Volatility Forecasting
- Predicts 21-day forward realised volatility to supply Monte Carlo's sigma
- 21 features per instrument: realised volatility at 5/10/21/63 days,
  Parkinson and Garman-Klass range estimators, momentum, RSI, drawdown
  and index context
- Every forecast is labelled `ml_predicted` or `historical_fallback`,
  so a fallback is never presented as a prediction
- **Distinct from the explanations above** — a trained regressor
  returning a number, not an LLM returning prose

### 📈 Stock Predictor
- A 21-trading-day outlook for any stock: current trend, probability of a
  rise, and an expected price range drawn as a fan chart
- Reports the stock's own **historical base rate** beside the probability,
  because most large stocks rise more often than they fall over a month
- **Direction was tested and found unpredictable.** Seven classifiers were
  scored on 4,390 untouched rows and none beat that base rate (best Brier
  skill −0.0012, 95% interval −0.014 to +0.011). So the probability shown
  *is* the base rate, labelled "Not a prediction", with the evidence one
  click away — rather than an unvalidated number dressed up as ML
- **The expected range is the validated part, and is the module's real
  output.** Backtested over 4,450 out-of-sample windows: the 95% band
  contained the price 94.8% of the time (nominal 95%), the 68% band 71.5%
  (nominal 68.3%). It also beats trailing realised volatility, which manages
  only 91.7% at the 95% level
- The range is centred on today's price: it shows how far, not which way
- An optional **Explain** button writes a plain-language reading with the
  local LLM; its output is checked by a deterministic guard that rejects
  advice and certainty, so the wording rules don't rest on the model's compliance

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13 (3.12 should work; 3.13.7 is what this is developed against)
- Node.js 18+
- [Ollama](https://ollama.com) — only needed for the AI explanation panels

### Installation

```bash
git clone <your-repo-url>
cd "AI Smart Investment Portfolio Advisor"
```

**Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
cp .env.example .env             # then set SECRET_KEY, see below
alembic upgrade head             # create / migrate the database
```

**Frontend**
```bash
cd frontend
npm install
```

**AI model** (optional — only for the explanation panels)
```bash
ollama pull qwen2.5:3b
```

**Generate a real `SECRET_KEY`.** The value in `.env.example` is a
placeholder and must not be used:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Run the Project

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Access Application:**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

---

## 📂 Project Structure

```
AI Smart Investment Portfolio Advisor/
│
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── api/                      # HTTP routers
│   │   │   ├── auth.py               # Register / login / me
│   │   │   ├── users.py              # User record (self only)
│   │   │   ├── profile.py            # Financial profile
│   │   │   ├── risk.py               # Risk assessment (rule-based)
│   │   │   ├── recommendation.py     # Asset allocation
│   │   │   ├── portfolio_analysis.py # Sharpe / drawdown / volatility
│   │   │   ├── diversification_analysis.py
│   │   │   ├── monte_carlo.py        # Simulation + VaR/CVaR
│   │   │   ├── sip.py                # SIP planning
│   │   │   ├── market.py             # Stock search / history
│   │   │   ├── ml.py                 # Volatility + trend outlook
│   │   │   └── ollama_health.py      # LLM health check
│   │   │
│   │   ├── core/
│   │   │   ├── config.py             # Settings from .env
│   │   │   ├── database.py           # SQLAlchemy engine/session
│   │   │   ├── dependencies.py       # Shared JWT dependency
│   │   │   └── security.py           # bcrypt + JWT
│   │   │
│   │   ├── ml/                       # Volatility + trend ML library
│   │   │   ├── README.md             # >> ML integration contract <<
│   │   │   ├── config.py             # Universe, horizon, paths
│   │   │   ├── data.py               # Cached yfinance loader
│   │   │   ├── features.py           # Features + target (shared!)
│   │   │   ├── evaluation.py         # RMSE/MAE/QLIKE + baselines
│   │   │   ├── model_registry.py     # Volatility artifact contract
│   │   │   ├── trend.py              # Up/down target, range, scoring
│   │   │   └── trend_registry.py     # Trend classifier artifact contract
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models (10)
│   │   ├── schemas/                  # Pydantic request/response
│   │   └── services/                 # Business logic
│   │       ├── ml_prediction_service.py  # Forecast + fallback chain
│   │       ├── stock_trend_service.py    # Stock Predictor outlook
│   │       ├── monte_carlo_simulator.py  # Geometric Brownian motion
│   │       ├── ollama_service.py         # LLM client
│   │       ├── ollama_prompts.py
│   │       ├── risk_calculator.py
│   │       ├── recommendation_engine.py
│   │       ├── portfolio_risk_analyzer.py
│   │       ├── diversification_analyzer.py
│   │       ├── sip_calculator.py
│   │       └── yahoo_finance_service.py
│   │
│   ├── alembic/                      # Database migrations
│   │   └── versions/
│   ├── tests/                        # pytest suite (406 tests)
│   ├── ml/                           # Offline dataset scripts
│   │   ├── generate_investor_dataset.py    # Synthetic (unused by app)
│   │   ├── prepare_volatility_dataset.py   # Real NSE price panel
│   │   └── prepare_trend_dataset.py        # Up/down labels, same features
│   ├── scripts/                      # Training / evaluation entry points
│   │   ├── train_volatility_model.py # Train, evaluate, conditionally save
│   │   └── evaluate_trend_classifier.py  # Direction: tests 7 models, saves only on a real edge
│   ├── models/                       # Trained artifacts (gitignored)
│   ├── data_cache/                   # Parquet price cache (gitignored)
│   ├── datasets/                     # Generated datasets (gitignored)
│   ├── .env.example                  # Copy to .env
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/                         # React 18 + Tailwind
│   ├── public/
│   ├── src/
│   │   ├── components/               # Layout + reusable UI
│   │   ├── context/AuthContext.js    # Auth state
│   │   ├── pages/                    # 15 pages
│   │   ├── services/                 # API clients
│   │   │   ├── api.js                # Shared axios instance
│   │   │   ├── mlService.js          # Volatility forecasting
│   │   │   └── ...
│   │   └── index.css
│   ├── .env                          # REACT_APP_API_BASE_URL
│   └── package.json
│
├── docs/
│   ├── deployment.md
│   ├── testing.md
│   └── modules/                      # Per-module reference docs
│
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL ORM
- **SQLite** - Lightweight database
- **Pydantic** - Data validation
- **yfinance** - Yahoo Finance API
- **NumPy/Pandas** - Data processing
- **scikit-learn** - Machine learning
- **Ollama** - Local AI inference (qwen2.5:3b)

### Frontend
- **React 18** - UI library
- **React Router** - Navigation
- **Recharts** - Data visualization
- **TailwindCSS** - Styling
- **Axios** - HTTP client

### AI/ML
- **Ollama** + **qwen2.5:3b** - local LLM for generated explanations (~2GB)
- **scikit-learn** - volatility forecasting model (trained offline, loaded via `joblib`)
- **arch** / **statsmodels** - GARCH(1,1) and HAR baselines the model is measured against
- **NumPy** - Monte Carlo simulation (geometric Brownian motion)
- **yfinance** - daily NSE price history, disk-cached to parquet

---

## 🧠 Machine Learning

The project contains **a synthetic dataset and two real ones**. Keeping
them straight matters, because one is real and one is not:

| | Synthetic investor dataset | Volatility panel | Trend panel |
|---|---|---|---|
| Source | `numpy` RNG, seed 42 | Yahoo Finance daily OHLCV | Yahoo Finance daily OHLCV |
| Size | 50,000 rows | 21 features, 10 NSE tickers | 21,990 rows × 21 features, 10 NSE tickers |
| Target | none that exists in the world | next-21-day realised volatility | closes higher in 21 days (0/1) |
| Built by | `ml/generate_investor_dataset.py` | `ml/prepare_volatility_dataset.py` | `ml/prepare_trend_dataset.py` |
| Used by the app? | **No** | Yes — feeds Monte Carlo's sigma | Yes — Stock Predictor |

The two real panels share the same 21 features (`app/ml/features.py`) and
differ only in the target.

The synthetic investor dataset generates its own labels from a weighted
scoring rule, so a classifier trained on it largely recovers that rule
plus noise. The equivalent logic already ships deterministically in
`app/services/risk_calculator.py`, which is why **Risk Assessment is
rule-based, not ML**. The dataset is retained for reference only.

The genuine ML work is **volatility forecasting**, with the **Stock
Predictor** as a second, more cautious use of the same pipeline:

- **Target**: realised volatility over the next 21 trading days,
  annualised. Not returns — daily and monthly returns are close to
  unpredictable from price history, whereas volatility clusters and
  persists, so a model can beat a naive baseline by a measurable margin.
- **Stock Predictor** does estimate direction, so it is held to a stricter
  standard: it reports the probability of a rise *beside the stock's own
  historical base rate*, scores models on Brier skill rather than accuracy,
  and says plainly when no model is loaded or a model fails to beat the
  base rate. On this dataset the training period rose in 58% of 21-day
  windows but the test period only 46%, so an "always up" predictor scores
  below a coin flip out of sample. See
  [docs/modules/stock-predictor.md](docs/modules/stock-predictor.md).
- **Baselines it must beat**: naive persistence ("next month equals this
  month"), HAR, and GARCH(1,1), scored on RMSE, MAE and QLIKE.
- **No API key is required** for market data; `yfinance` reads public
  endpoints and results are cached to parquet.

Training happens offline and the artifact is loaded at runtime. The full
contract — feature parity, the chronological split with its embargo, the
baselines, and how to save a model the API will accept — is in
**[backend/app/ml/README.md](backend/app/ml/README.md)**.

To train the volatility model, run `python scripts/train_volatility_model.py`
from `backend/` (add `--dry-run` to evaluate without saving, `--garch` to
include the slow GARCH baseline). It saves only if the model beats naive
persistence on both RMSE and QLIKE, and it verifies that the date-based
embargo really is 21 trading dates rather than trusting it.

To re-run the direction experiment, run
`python scripts/evaluate_trend_classifier.py` from `backend/`. It trains
seven classifiers, scores them on Brier skill against the training-period
base rate (never against 50%), and puts a 95% block-bootstrap interval on
the best one. It saves a model **only** if that interval excludes zero, so
a merely-lucky candidate cannot reach the Stock Predictor. On the current
data nothing qualifies, and the script says so.

```bash
POST /api/ml/predict-volatility   {"ticker": "RELIANCE.NS"}
GET  /api/ml/model-info           # is a volatility model loaded, and which
GET  /api/ml/trend-outlook/RELIANCE.NS   # Stock Predictor
GET  /api/ml/trend-model-info            # is a trend classifier loaded
```

---

## 📊 Data Flow

```
User Input → React Frontend → FastAPI Backend → Services Layer
                                     ↓
                              ┌──────────────┐
                              │   Database   │
                              │   (SQLite)   │
                              └──────────────┘
                                     ↓
                              ┌──────────────┐
                              │  AI Service  │
                              │   (Ollama)   │
                              └──────────────┘
                                     ↓
                              ┌──────────────┐
                              │ Market Data  │
                              │ (Yahoo API)  │
                              └──────────────┘
                                     ↓
                              AI-Enhanced Response → Frontend
```

---

## 🎯 Use Cases

### 1. New Investor
- Create account and financial profile
- Get automated risk assessment
- Receive AI-powered portfolio recommendations
- Start SIP with goal-based planning

### 2. Active Investor
- Track existing portfolio performance
- Analyze diversification and risk metrics
- Run Monte Carlo simulations for future projections
- Get AI insights on market trends

### 3. Retirement Planning
- Set retirement goal with time horizon
- Calculate required monthly SIP
- Simulate best/worst case scenarios
- Monitor progress with analytics

### 4. Wealth Creation
- Define wealth creation goals
- Get aggressive growth strategies
- Track high-growth stocks
- Optimize portfolio allocation

---

## 🔒 Security Features

- JWT-based authentication (HS256), required on every data endpoint
- **bcrypt password hashing** (cost factor 12)
- Per-user data scoping - every query filters on the authenticated user
- CORS restricted to configured origins
- SQL injection prevention via SQLAlchemy parameter binding

> ⚠️ **Before deploying publicly:**
> - Set a real `SECRET_KEY` (see Installation) and `DEBUG=False`
> - Remove the plain-text fallback in `verify_password`
>   (`backend/app/core/security.py`), which exists only so dev accounts
>   created before hashing was enabled still work
> - Move off SQLite to PostgreSQL
> - `POST /api/ml/reload-model` is currently open to any authenticated
>   user and should be restricted to an admin role

---

## 📈 Performance Optimizations

### Backend
- Async/await for I/O operations
- Database query optimization
- Caching for AI explanations
- Connection pooling
- Response compression

### Frontend
- Code splitting
- Lazy loading
- React.memo for components
- localStorage for persistence
- Optimistic UI updates

### AI Service
- Local inference (no API costs)
- 3B model for speed (5-15s responses)
- Caching of generated insights
- Configurable timeouts

---

## 🧪 Testing

### Automated tests
```bash
cd backend
pytest                 # 406 tests
```

Covers the Monte Carlo simulator's maths (including closed-form drift
checks), feature-engineering leakage guards, the model artifact contract
and the volatility fallback chain.

### Manual testing
Register an account through the UI at http://localhost:3000/register.
Each analytics page has a **Generate Sample Data** button to populate it.

### Datasets
```bash
cd backend
python ml/generate_investor_dataset.py       # 50,000 synthetic investor profiles
python -m ml.prepare_volatility_dataset      # real NSE price panel for volatility training
python scripts/train_volatility_model.py --dry-run   # train + evaluate the volatility model, saves nothing
python scripts/evaluate_trend_classifier.py          # can direction beat the base rate? (expected answer: no)
```

These are two unrelated datasets - see **Machine Learning** below.

---

## 📚 Documentation

- **System architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **ML integration contract**: [backend/app/ml/README.md](backend/app/ml/README.md)
- **Module reference**: [docs/modules/](docs/modules/) -
  [financial profile](docs/modules/financial-profile.md) |
  [risk profiling](docs/modules/risk-profiling.md) |
  [recommendation](docs/modules/portfolio-recommendation.md) |
  [analytics](docs/modules/portfolio-analytics.md) |
  [diversification](docs/modules/diversification.md) |
  [Monte Carlo](docs/modules/monte-carlo.md) |
  [SIP planner](docs/modules/sip-planner.md) |
  [stock explorer](docs/modules/stock-explorer.md) |
  [stock predictor](docs/modules/stock-predictor.md)
- **Deployment**: [docs/deployment.md](docs/deployment.md)
- **Testing**: [docs/testing.md](docs/testing.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Live API docs**: http://localhost:8000/docs (when running)

---

## 🐛 Known Issues & Limitations

### Current Limitations
1. **Stock data**: `yfinance` is an unofficial scraper, not a supported
   API. It can be rate-limited or break when Yahoo changes its pages, and
   the data is not licensed for commercial redistribution. History is
   cached to `backend/data_cache/`, and the loader serves a stale cache
   rather than failing.
2. **The volatility model is trained locally and not committed.** Model
   files are git-ignored, so a fresh clone has none and
   `/api/ml/predict-volatility` returns trailing realised volatility labelled
   `source: "historical_fallback"` until you run
   `python scripts/train_volatility_model.py`. The first run (a ridge
   regression on log-volatility) cut error against naive persistence clearly
   (RMSE 17.8% lower, QLIKE 46.4% lower) but was **not statistically
   distinguishable from the HAR baseline** (QLIKE 4.3% lower, 95% interval
   -2.8% to +10.8%), and its forecasts are compressed toward the average.
   See the [ML integration contract](backend/app/ml/README.md).
3. **AI model**: `qwen2.5:3b` is lightweight and noticeably weaker than
   7b/14b. On CPU it generates ~10 tokens/sec, so a first explanation
   takes 90-120s; results are cached per record afterwards.
4. **Database**: SQLite. Fine for development, not for production.
5. **Monte Carlo assumptions**: constant return and volatility over the
   horizon, a single portfolio-level sigma, and no covariance between
   holdings.
6. **`POST /api/ml/reload-model`** is available to any authenticated
   user; it needs an admin role.
7. **`verify_password` retains a plain-text fallback** so dev accounts
   predating bcrypt still work. Remove it before production.
8. **Sector is resolved from market data, not stored.** A transaction
   records the asset type but not the sector, so sectors are looked up
   from the market-data provider for holdings that have a ticker (gold
   and bonds are treated as their own sector). A holding with no ticker
   — unlisted equity, a fund without a symbol — stays `Unclassified`
   rather than being guessed, and the Diversification page reports what
   share of the portfolio by value that affects.
9. **Two different return figures, on purpose.** Portfolio Tracking shows a
   simple return on what you put in (money-weighted, what your money did).
   Portfolio Analytics shows a time-weighted return that strips out
   deposits (what the investments did). They will not match, and both are
   correct for their question. XIRR is future work.
10. **Cost basis is average-cost only.** FIFO and tax-lot tracking (needed
    for Indian LTCG/STCG reporting) are not implemented.

### Troubleshooting
- **Frontend takes 3+ minutes to compile the first time** on Windows.
  That is normal for Create React App on a cold cache, not a hang.
- **An AI panel appears stuck**: it is probably still generating. Allow
  up to two minutes on a cache miss.
- **401 responses everywhere**: every data endpoint requires a JWT. Log
  in; the token is stored as `access_token`.
- Check backend logs for API errors, and verify Ollama is running
  (`curl http://localhost:11434/api/tags`) for AI features.

---

## 🚧 Roadmap / Future Enhancements

### Phase 1 (Completed) ✅
- [x] User authentication
- [x] Financial profile management
- [x] Risk assessment with AI
- [x] Portfolio recommendations
- [x] Portfolio tracking (transaction ledger, derived holdings, live P&L)
- [x] Portfolio analytics
- [x] Diversification analysis
- [x] Monte Carlo simulations
- [x] SIP calculator
- [x] Stock explorer
- [x] AI-powered insights

### Phase 2 (In progress) 🔄
- [x] ML integration seam — feature pipeline, artifact contract,
      prediction service with fallback, `/api/ml/*` endpoints
- [x] Geometric Brownian motion Monte Carlo with VaR/CVaR
- [x] Alembic migrations, 406 automated tests
- [x] **Volatility model trained and evaluated** against naive persistence,
      HAR and GARCH(1,1) (`scripts/train_volatility_model.py`); the artifact
      is local, not committed
- [x] **Stock Predictor trend classifier evaluated — no edge found.** Seven
      candidates (logistic regression, random forest, gradient boosting) scored
      on 4,390 untouched rows; none beat the historical base rate. Best Brier
      skill -0.0012, 95% interval -0.014 to +0.011. Reproduce with
      `scripts/evaluate_trend_classifier.py`; it deploys a model automatically
      if one ever clears the bar
- [ ] XIRR / time-weighted returns, and FIFO tax-lot tracking
- [ ] Advanced portfolio optimization algorithms
- [ ] Tax optimization strategies
- [ ] Multi-currency support
- [ ] Mobile responsive design improvements
- [ ] Export reports (PDF/Excel)
- [ ] Email notifications
- [ ] Social sharing features

### Phase 3 (Future) 🌟
- [ ] Real-time portfolio sync with brokers
- [ ] Automated rebalancing
- [ ] Advanced backtesting
- [ ] Community features
- [ ] Mobile apps (iOS/Android)
- [ ] Crypto portfolio tracking
- [ ] ESG investment filters

---

## 🤝 Contributing

This is a complete, production-ready project. For modifications:

1. **Backend Changes**: Modify files in `backend/app/`
2. **Frontend Changes**: Modify files in `frontend/src/`
3. **ML Features**: Add scripts to `backend/ml/`
4. **Database Schema**: Update models in `backend/app/models/`

### Development Workflow
```bash
# Backend development
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Frontend development
cd frontend
npm start

# Dataset regeneration
cd backend
python ml/generate_investor_dataset.py
```

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - For the excellent web framework
- **React** - For the powerful UI library
- **Ollama** - For making local AI inference accessible
- **Yahoo Finance** - For providing free market data
- **TailwindCSS** - For beautiful, responsive styling

---

## 📞 Support

For setup issues or questions:
1. See **Troubleshooting** under Known Issues above
2. Review backend logs for API errors
3. Verify dependencies installed cleanly (`pip install -r requirements.txt`)
4. Ensure Ollama is running for AI features
   (`curl http://localhost:11434/api/tags`)
5. Open an issue with the error output and your Python/Node versions

---

## 📊 Project Statistics

- **Backend endpoints**: 69 operations across 54 paths
- **Frontend pages**: 15
- **Database tables**: 10 (+ Alembic migrations)
- **Automated tests**: 406
- **AI explanation endpoints**: 8 (`/api/*/explain`)
- **Volatility features**: 21, over a 10-ticker NSE panel
- **Synthetic investor dataset**: 50,000 rows (unused by the app — see
  Machine Learning)

---

**Built with Python, React, and a local LLM**

**Version**: 1.0.0  
**Last Updated**: October 2026  
**Status**: Functional. The volatility model is trained locally (not committed). A trend classifier was evaluated and rejected: none of seven candidates beat the historical base rate, so the Stock Predictor shows that base rate, labelled honestly, and derives its value from the validated expected price range.

---

## 🎉 Getting Started

1. Follow **Quick Start** above to install and run both servers
2. Register an account at http://localhost:3000/register
3. Fill in your financial profile, then run Risk Assessment to get an
   investor type and a recommended allocation
4. Use **Generate Sample Data** on the analytics pages to populate them
5. Try Monte Carlo — switch the volatility source to *ML-based forecast*
   to see the provenance banner in action

Planning to train the volatility model? Start with
[backend/app/ml/README.md](backend/app/ml/README.md).
