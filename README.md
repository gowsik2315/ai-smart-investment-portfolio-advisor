# 🎯 AI Smart Investment Portfolio Advisor

> An intelligent investment portfolio management system powered by AI, providing personalized recommendations, risk analysis, and portfolio optimization.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-118%20passing-brightgreen.svg)](backend/tests/)
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

### 📈 Portfolio Analytics
- Real-time performance tracking
- Returns calculation (daily, weekly, monthly, yearly)
- Risk metrics (Sharpe ratio, volatility, beta)
- Benchmark comparison

### 🌈 Diversification Analysis
- Sector diversification scoring
- Asset class distribution
- Concentration risk identification
- Optimization recommendations

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
│   │   │   ├── ml.py                 # Volatility forecasting
│   │   │   └── ollama_health.py      # LLM health check
│   │   │
│   │   ├── core/
│   │   │   ├── config.py             # Settings from .env
│   │   │   ├── database.py           # SQLAlchemy engine/session
│   │   │   ├── dependencies.py       # Shared JWT dependency
│   │   │   └── security.py           # bcrypt + JWT
│   │   │
│   │   ├── ml/                       # Volatility forecasting library
│   │   │   ├── README.md             # >> ML integration contract <<
│   │   │   ├── config.py             # Universe, horizon, paths
│   │   │   ├── data.py               # Cached yfinance loader
│   │   │   ├── features.py           # Features + target (shared!)
│   │   │   ├── evaluation.py         # RMSE/MAE/QLIKE + baselines
│   │   │   └── model_registry.py     # Artifact save/load contract
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models (10)
│   │   ├── schemas/                  # Pydantic request/response
│   │   └── services/                 # Business logic
│   │       ├── ml_prediction_service.py  # Forecast + fallback chain
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
│   ├── tests/                        # pytest suite (118 tests)
│   ├── ml/                           # Offline dataset scripts
│   │   ├── generate_investor_dataset.py    # Synthetic (unused by app)
│   │   └── prepare_volatility_dataset.py   # Real NSE price panel
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
│   │   ├── pages/                    # 14 pages
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

The project contains **two unrelated datasets**. Keeping them straight
matters, because one is real and one is not:

| | Synthetic investor dataset | Volatility panel |
|---|---|---|
| Source | `numpy` RNG, seed 42 | Yahoo Finance daily OHLCV |
| Size | 50,000 rows | 9,680 rows × 21 features, 10 NSE tickers |
| Built by | `ml/generate_investor_dataset.py` | `ml/prepare_volatility_dataset.py` |
| Used by the app? | **No** | Yes — feeds Monte Carlo's sigma |

The synthetic investor dataset generates its own labels from a weighted
scoring rule, so a classifier trained on it largely recovers that rule
plus noise. The equivalent logic already ships deterministically in
`app/services/risk_calculator.py`, which is why **Risk Assessment is
rule-based, not ML**. The dataset is retained for reference only.

The genuine ML work is **volatility forecasting**:

- **Target**: realised volatility over the next 21 trading days,
  annualised. Not returns — daily and monthly returns are close to
  unpredictable from price history, whereas volatility clusters and
  persists, so a model can beat a naive baseline by a measurable margin.
- **Baselines it must beat**: naive persistence ("next month equals this
  month"), HAR, and GARCH(1,1), scored on RMSE, MAE and QLIKE.
- **No API key is required** for market data; `yfinance` reads public
  endpoints and results are cached to parquet.

Training happens offline and the artifact is loaded at runtime. The full
contract — feature parity, the chronological split with its embargo, the
baselines, and how to save a model the API will accept — is in
**[backend/app/ml/README.md](backend/app/ml/README.md)**.

```bash
POST /api/ml/predict-volatility   {"ticker": "RELIANCE.NS"}
GET  /api/ml/model-info           # is a model loaded, and which
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
pytest                 # 118 tests
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
  [stock explorer](docs/modules/stock-explorer.md)
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
2. **No volatility model is shipped.** `/api/ml/predict-volatility`
   returns trailing realised volatility labelled
   `source: "historical_fallback"` until one is trained. See the
   [ML integration contract](backend/app/ml/README.md).
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
- [x] Portfolio tracking and analytics
- [x] Diversification analysis
- [x] Monte Carlo simulations
- [x] SIP calculator
- [x] Stock explorer
- [x] AI-powered insights

### Phase 2 (In progress) 🔄
- [x] ML integration seam — feature pipeline, artifact contract,
      prediction service with fallback, `/api/ml/*` endpoints
- [x] Geometric Brownian motion Monte Carlo with VaR/CVaR
- [x] Alembic migrations, 118 automated tests
- [ ] **Train and evaluate the volatility model** against the naive,
      HAR and GARCH(1,1) baselines — the remaining step
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

- **Backend endpoints**: 54 operations across 43 paths
- **Frontend pages**: 14
- **Database tables**: 10 (+ Alembic migrations)
- **Automated tests**: 118
- **AI explanation endpoints**: 7 (`/api/*/explain`)
- **Volatility features**: 21, over a 10-ticker NSE panel
- **Synthetic investor dataset**: 50,000 rows (unused by the app — see
  Machine Learning)

---

**Built with Python, React, and a local LLM**

**Version**: 1.0.0  
**Last Updated**: October 2026  
**Status**: Functional; the volatility model is not yet trained

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
