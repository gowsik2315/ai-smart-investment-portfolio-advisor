# Smart Investment Advisor - Backend

FastAPI backend for the AI-Powered Smart Investment Portfolio Advisor.

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env file and update configuration
```

### 5. Initialize Database

```bash
python -m app.db_init
```

### 6. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   ├── core/             # Core configurations
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── main.py           # Application entry point
│   └── db_init.py        # Database initialization
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### User Profile
- `GET /api/users/{user_id}` - Get user by ID
- `PUT /api/users/{user_id}` - Update user

### Financial Profile
- `POST /api/profile/` - Create financial profile
- `GET /api/profile/{user_id}` - Get financial profile
- `PUT /api/profile/{user_id}` - Update financial profile

### Risk Assessment (Phase 2)
- `POST /api/risk/assess` - Assess risk profile
- `GET /api/risk/profile/{user_id}` - Get risk profile

### Portfolio (Phase 2)
- `GET /api/portfolio/recommend` - Get recommendations
- `GET /api/portfolio/current/{user_id}` - Get current portfolio
- `POST /api/portfolio/simulate` - Simulate portfolio growth

### SIP Plans (Phase 2)
- `POST /api/sip/plan` - Create SIP plan
- `GET /api/sip/plans/{user_id}` - Get user SIP plans

### Market Data (Phase 2)
- `GET /api/market/stocks` - Search stocks
- `GET /api/market/stock/{symbol}` - Get stock details

## Database Models

- **Users** - User authentication and profile
- **FinancialProfiles** - User financial information
- **RiskProfiles** - Risk assessment results
- **Portfolios** - Investment portfolios
- **SIPPlans** - Systematic investment plans
- **Transactions** - Investment transactions

## Development

### Running Tests

```bash
pytest
```

### Code Style

Follow PEP 8 guidelines for Python code.

## Notes

- Phase 1 includes basic architecture and authentication
- Business logic will be implemented in Phase 2
- Use SQLite for development, can be switched to PostgreSQL for production
