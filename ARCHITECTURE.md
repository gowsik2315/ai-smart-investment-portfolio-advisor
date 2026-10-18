# System Architecture Document
# AI-Powered Smart Investment Portfolio Advisor

## 1. System Overview

The Smart Investment Portfolio Advisor is a full-stack web application that provides AI-powered investment recommendations, risk assessment, and portfolio management capabilities.

### Technology Stack

**Frontend:**
- React.js 18.2.0
- React Router 6.21.1
- Tailwind CSS 3.4.1
- Axios 1.6.5
- Recharts 2.10.3

**Backend:**
- FastAPI 0.141.1
- Python 3.13
- SQLAlchemy 2.0.52 + Alembic 1.19.1 (migrations)
- SQLite (development) / PostgreSQL (production)

**Data Sources:**
- Yahoo Finance via `yfinance` (unofficial scraper, no API key),
  disk-cached to parquet under `backend/data_cache/`

**AI / ML:**
- Ollama + `qwen2.5:3b` for generated explanations (`/api/*/explain`)
- scikit-learn volatility forecasting model, trained offline and loaded
  at runtime via joblib (`/api/ml/*`)
- `arch` / `statsmodels` for the GARCH and HAR baselines
- These are two separate subsystems: one produces prose, the other a
  number. Neither depends on the other.

**Authentication:**
- JWT (JSON Web Tokens)
- Bcrypt (Password Hashing)

---

## 2. Architecture Patterns

### 2.1 Overall Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│   React.js      │◄───────►│   FastAPI       │◄───────►│   SQLite DB     │
│   Frontend      │  HTTP   │   Backend       │  ORM    │   Database      │
│                 │  REST   │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                     │
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   Yahoo Finance │
                            │   (yfinance)    │
                            └─────────────────┘
```

### 2.2 Frontend Architecture

```
┌──────────────────────────────────────────────────────┐
│                    React Application                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │   Pages    │  │ Components │  │  Context   │    │
│  │            │  │            │  │            │    │
│  │ - Home     │  │ - Layout   │  │ - Auth     │    │
│  │ - Login    │  │ - Common   │  └────────────┘    │
│  │ - Register │  │ - Widgets  │                     │
│  │ - Dashboard│  └────────────┘                     │
│  └────────────┘                                      │
│         │                                            │
│         ▼                                            │
│  ┌────────────────────────────────┐                 │
│  │      Services Layer            │                 │
│  │  - API Service                 │                 │
│  │  - Auth Service                │                 │
│  │  - Profile Service             │                 │
│  └────────────────────────────────┘                 │
│         │                                            │
│         ▼                                            │
│  ┌────────────────────────────────┐                 │
│  │      Axios HTTP Client         │                 │
│  └────────────────────────────────┘                 │
└──────────────────────────────────────────────────────┘
```

### 2.3 Backend Architecture

```
┌──────────────────────────────────────────────────────┐
│                  FastAPI Application                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────────────────────────────┐     │
│  │            API Routes (Controllers)        │     │
│  │  - auth.py    - portfolio.py              │     │
│  │  - users.py   - sip.py                    │     │
│  │  - profile.py - market.py                 │     │
│  │  - risk.py                                 │     │
│  └────────────────────────────────────────────┘     │
│         │                                            │
│         ▼                                            │
│  ┌────────────────────────────────────────────┐     │
│  │          Services (Business Logic)         │     │
│  │  - Risk Profiling Engine                   │     │
│  │  - Portfolio Recommendation Engine         │     │
│  │  - SIP Calculator                          │     │
│  │  - Market Data Service                     │     │
│  └────────────────────────────────────────────┘     │
│         │                                            │
│         ▼                                            │
│  ┌────────────────────────────────────────────┐     │
│  │       Data Access Layer (SQLAlchemy)       │     │
│  │  - Models (ORM)                            │     │
│  │  - Schemas (Pydantic)                      │     │
│  └────────────────────────────────────────────┘     │
│         │                                            │
│         ▼                                            │
│  ┌────────────────────────────────────────────┐     │
│  │              SQLite Database               │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
```

---

## 3. Database Schema

### 3.1 Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────────┐
│    Users    │         │ FinancialProfiles│
│─────────────│         │──────────────────│
│ id (PK)     │────────<│ id (PK)          │
│ email       │    1:1  │ user_id (FK)     │
│ password    │         │ age              │
│ full_name   │         │ income           │
│ created_at  │         │ savings          │
└─────────────┘         │ ...              │
       │                └──────────────────┘
       │
       │ 1:1
       │
       ▼
┌──────────────────┐
│  RiskProfiles    │
│──────────────────│
│ id (PK)          │
│ user_id (FK)     │
│ risk_score       │
│ risk_category    │
│ ...              │
└──────────────────┘

       │
       │ 1:N
       │
       ▼
┌──────────────────┐
│   Portfolios     │
│──────────────────│
│ id (PK)          │
│ user_id (FK)     │
│ portfolio_name   │
│ allocation       │
│ ...              │
└──────────────────┘

       │
       │ 1:N
       │
       ▼
┌──────────────────┐
│    SIPPlans      │
│──────────────────│
│ id (PK)          │
│ user_id (FK)     │
│ amount           │
│ frequency        │
│ ...              │
└──────────────────┘

       │
       │ 1:N
       │
       ▼
┌──────────────────┐
│  Transactions    │
│──────────────────│
│ id (PK)          │
│ user_id (FK)     │
│ portfolio_id(FK) │
│ type             │
│ amount           │
│ ...              │
└──────────────────┘
```

### 3.2 Table Descriptions

**users**
- Stores user authentication and basic profile information
- Primary entity for the system

**financial_profiles**
- One-to-one relationship with users
- Stores detailed financial information
- Used for risk assessment and recommendations

**risk_profiles**
- One-to-one relationship with users
- Stores risk assessment results
- Determines investment strategy

**portfolios**
- One-to-many relationship with users
- Stores portfolio configurations and allocations
- Tracks portfolio performance

**sip_plans**
- One-to-many relationship with users
- Stores systematic investment plan details
- Tracks SIP progress and projections

**transactions**
- One-to-many relationship with users and portfolios
- Records all investment transactions
- Audit trail for portfolio changes

---

## 4. API Architecture

### 4.1 RESTful API Design

**Base URL:** `http://localhost:8000/api`

**Authentication:**
- JWT tokens in Authorization header
- Format: `Authorization: Bearer <token>`

### 4.2 API Endpoints Structure

Generated from the live OpenAPI schema. Every endpoint below except
`/auth/register` and `/auth/login` requires a bearer token.

```
/api
├── /auth
│   ├── POST   /register                             # Register
│   ├── POST   /login                                # Login
│   └── GET    /me                                   # Read Current User
├── /users
│   ├── GET    /{user_id}                            # Get User
│   └── PUT    /{user_id}                            # Update User
├── /profile
│   ├── POST   /                                     # Create Financial Profile
│   ├── GET    /                                     # Get Financial Profile
│   ├── PUT    /                                     # Update Financial Profile
│   └── DELETE /                                     # Delete Financial Profile
├── /risk
│   ├── POST   /calculate                            # Calculate Risk Profile
│   ├── GET    /                                     # Get Risk Profile
│   ├── DELETE /                                     # Delete Risk Profile
│   └── GET    /explain                              # Explain Risk Profile
├── /recommendation
│   ├── POST   /generate                             # Generate Recommendation
│   ├── GET    /                                     # Get Recommendation
│   ├── DELETE /                                     # Delete Recommendation
│   └── GET    /explain                              # Explain Recommendation
├── /portfolio-analysis
│   ├── POST   /analyze                              # Analyze Portfolio
│   ├── GET    /latest                               # Get Latest Analysis
│   ├── POST   /generate-sample-data                 # Generate Sample Data
│   └── GET    /explain                              # Explain Portfolio Analysis
├── /diversification-analysis
│   ├── POST   /analyze                              # Analyze Diversification
│   ├── GET    /latest                               # Get Latest Analysis
│   ├── GET    /history                              # Get Analysis History
│   ├── POST   /generate-sample-holdings             # Generate Sample Holdings
│   ├── DELETE /{analysis_id}                        # Delete Analysis
│   └── GET    /explain                              # Explain Diversification Analysis
├── /monte-carlo
│   ├── POST   /simulate                             # Run Simulation
│   ├── GET    /simulations                          # Get Simulations
│   ├── GET    /simulations/{simulation_id}          # Get Simulation
│   ├── DELETE /simulations/{simulation_id}          # Delete Simulation
│   ├── PUT    /simulations/{simulation_id}          # Update Simulation
│   ├── GET    /latest                               # Get Latest Simulation
│   └── GET    /explain                              # Explain Monte Carlo Simulation
├── /sip
│   ├── POST   /calculate                            # Calculate Sip
│   ├── POST   /explain                              # Explain Sip Calculation
│   ├── POST   /plans                                # Create Sip Plan
│   ├── GET    /plans                                # Get Sip Plans
│   ├── GET    /plans/{plan_id}                      # Get Sip Plan
│   ├── PUT    /plans/{plan_id}                      # Update Sip Plan
│   └── DELETE /plans/{plan_id}                      # Delete Sip Plan
├── /market
│   ├── GET    /search                               # Search Stocks
│   ├── GET    /stock/{ticker}                       # Get Stock Info
│   ├── GET    /stock/{ticker}/history               # Get Stock History
│   ├── GET    /stock/{ticker}/outlook/explain       # Explain Stock Outlook
│   └── GET    /stock/{ticker}/explain               # Explain Stock Trend
├── /ml
│   ├── POST   /predict-volatility                   # Predict Volatility
│   ├── GET    /model-info                           # Get Model Info
│   ├── POST   /reload-model                         # Reload Model
│   ├── GET    /features/{ticker}                    # Get Feature Snapshot
│   ├── GET    /trend-outlook/{ticker}               # Get Trend Outlook
│   ├── GET    /trend-model-info                     # Get Trend Model Info
│   ├── POST   /reload-trend-model                   # Reload Trend Model
│   └── GET    /cache-status                         # Get Cache Status
└── /ollama
    ├── GET    /health                               # Check Ollama Health
    └── GET    /test                                 # Test Ollama Generation
```

### 4.3 Request/Response Flow

```
Client                  Backend                Database
  │                       │                      │
  │─────Request──────────>│                      │
  │  (HTTP + JWT)         │                      │
  │                       │                      │
  │                       │──Validate Token────> │
  │                       │                      │
  │                       │──Query/Update───────>│
  │                       │                      │
  │                       │<─────Result──────────│
  │                       │                      │
  │<────Response──────────│                      │
  │  (JSON)               │                      │
```

---

## 5. Security Architecture

### 5.1 Authentication Flow

```
1. User Registration
   ├── User submits registration form
   ├── Backend validates input
   ├── Password is hashed using bcrypt
   ├── User record created in database
   └── Success response returned

2. User Login
   ├── User submits credentials
   ├── Backend verifies email exists
   ├── Password hash compared
   ├── JWT access token generated
   ├── JWT refresh token generated
   └── Tokens returned to client

3. Protected Request
   ├── Client sends request with JWT
   ├── Backend validates JWT signature
   ├── Backend checks expiration
   ├── User ID extracted from token
   ├── Request processed
   └── Response returned
```

### 5.2 Security Measures

**Frontend:**
- XSS Protection (React escapes by default)
- HTTPS enforcement (production)
- Token storage in localStorage
- Automatic token refresh
- CORS configuration

**Backend:**
- Password hashing (bcrypt)
- JWT token authentication
- Token expiration
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- Rate limiting (future)

---

## 6. Component Architecture

### 6.1 Frontend Components

**Layout Components:**
- `Layout` - Main layout wrapper
- `Navbar` - Navigation bar
- `Footer` - Page footer

**Common Components:**
- `Card` - Reusable card container
- `Button` - Button with variants
- `Input` - Form input field
- `Loading` - Loading spinner

**Page Components:**
- `Home` - Landing page
- `Login` - Authentication page
- `Register` - Registration page
- `Dashboard` - Main dashboard
- `FinancialProfile` - Profile form
- `RiskAssessment` - Risk questionnaire
- `Portfolio` - Portfolio management
- `SIPPlanner` - SIP planning

### 6.2 State Management

**Context Providers:**
- `AuthContext` - Global authentication state
  - user
  - loading
  - login()
  - register()
  - logout()
  - isAuthenticated

**Future Contexts (Phase 2):**
- `ProfileContext` - Financial profile state
- `PortfolioContext` - Portfolio data state
- `ThemeContext` - Theme preferences

---

## 7. Data Flow

### 7.1 User Registration Flow

```
User Form → Validation → API Request → Backend Validation
    ↓
Password Hash → Database Insert → Success Response
    ↓
Redirect to Login
```

### 7.2 User Login Flow

```
Login Form → API Request → Verify Credentials → Generate JWT
    ↓
Store Tokens → Update Auth Context → Redirect to Dashboard
```

### 7.3 Financial Profile Submission Flow

```
Profile Form → Validation → API Request → Create/Update Profile
    ↓
Trigger Risk Assessment → Calculate Risk Score → Generate Recommendations
    ↓
Update UI with Results
```

---

## 8. Scalability Considerations

### 8.1 Current Architecture

- **Database:** SQLite (single file, good for development)
- **Deployment:** Single server
- **Sessions:** JWT (stateless)

### 8.2 Future Scaling Strategy

**Database:**
- Migrate to PostgreSQL
- Read replicas for queries
- Sharding by user_id

**Caching:**
- Redis for session data
- Cache market data
- Cache recommendation results

**Load Balancing:**
- Multiple backend instances
- Nginx load balancer
- Horizontal scaling

**Microservices (Phase 3):**
- Risk Assessment Service
- Portfolio Recommendation Service
- Market Data Service
- Notification Service

---

## 9. Technology Choices Rationale

### 9.1 Why FastAPI?

- **Fast:** High performance, async support
- **Easy:** Automatic API documentation
- **Type Safe:** Pydantic validation
- **Modern:** Python 3.13 features

### 9.2 Why React?

- **Component-Based:** Reusable UI components
- **Ecosystem:** Large library ecosystem
- **Performance:** Virtual DOM optimization
- **Developer Experience:** Hot reload, dev tools

### 9.3 Why SQLite?

- **Simplicity:** Zero configuration
- **Portability:** Single file database
- **Performance:** Good for < 100K records
- **Development:** Easy setup and testing

### 9.4 Why Tailwind CSS?

- **Utility-First:** Rapid UI development
- **Customizable:** Easy theming
- **Small Bundle:** Purges unused CSS
- **Responsive:** Mobile-first design

---

## 10. Development Phases

### Phase 1: Foundation ✅
- Project setup
- Basic authentication
- Database models
- UI components
- API structure

### Phase 2: Core Features ✅
- Risk profiling engine
- Portfolio recommendations
- SIP calculator
- Market data integration
- Dashboard with real data

### Phase 3: Advanced Features 🔄
- ✅ Monte Carlo simulation (geometric Brownian motion, VaR/CVaR)
- ✅ Diversification and portfolio risk analytics
- ✅ AI-generated explanations (Ollama), cached per record
- ✅ ML integration layer: shared feature pipeline, artifact contract,
     prediction service with fallback, `/api/ml/*` endpoints
- ✅ Volatility model trained and evaluated against naive persistence, HAR and
     GARCH(1,1) (`scripts/train_volatility_model.py`); the artifact is local
- ⬜ Real-time data, performance tracking, notifications

### Phase 4: Production 🔄
- ✅ Automated tests (336, pytest)
- ✅ Alembic migrations
- ✅ Per-user authorization on every data endpoint
- ⬜ Security audit, PostgreSQL migration, deployment, monitoring

---

## 11. Deployment Architecture (Future)

```
┌──────────────────────────────────────────────────────┐
│                   Load Balancer                       │
│                      (Nginx)                          │
└─────────────────┬────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   Frontend    │   │   Frontend    │
│   (Vercel)    │   │   (Vercel)    │
└───────────────┘   └───────────────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   API Gateway   │
        └─────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   Backend 1   │   │   Backend 2   │
│   (FastAPI)   │   │   (FastAPI)   │
└───────────────┘   └───────────────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   PostgreSQL    │
        │   (Managed DB)  │
        └─────────────────┘
```

---

## Summary

This architecture provides:
- ✅ Separation of concerns (Frontend/Backend)
- ✅ RESTful API design
- ✅ Secure authentication (JWT)
- ✅ Scalable database schema
- ✅ Modular component structure
- ✅ Clear data flow
- ✅ Future-proof design

The system is built with modern best practices and can scale from development to production deployment.
