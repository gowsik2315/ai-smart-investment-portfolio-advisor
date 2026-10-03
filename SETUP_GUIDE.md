# Complete Setup Guide
# AI-Powered Smart Investment Portfolio Advisor

This guide will walk you through setting up the entire application from scratch.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.9 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**
- **Git** (optional) - [Download](https://git-scm.com/)

### Verify Installation

```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check npm version
npm --version
```

## Project Structure Overview

```
smart-investment-advisor/
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── README.md          # Project overview
└── SETUP_GUIDE.md     # This file
```

---

## Part 1: Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- SQLAlchemy (database ORM)
- Pydantic (data validation)
- Python-Jose (JWT tokens)
- Passlib (password hashing)
- And other dependencies

### Step 4: Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

**Edit the `.env` file:**

```env
DATABASE_URL=sqlite:///./investment_advisor.db
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**⚠️ Important:** Generate a secure SECRET_KEY for production:

```bash
# Generate a secure secret key (run in Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Initialize Database

```bash
python -m app.db_init
```

This will create:
- SQLite database file (`investment_advisor.db`)
- All required tables (users, financial_profiles, risk_profiles, portfolios, sip_plans, transactions)

### Step 6: Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend is now running at:**
- API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Step 7: Test Backend

Open your browser and visit http://localhost:8000/docs

You should see the FastAPI interactive documentation with all available endpoints.

**Keep this terminal window open** and proceed to frontend setup in a new terminal.

---

## Part 2: Frontend Setup

### Step 1: Open New Terminal

Open a new terminal window/tab (keep backend running in the previous terminal).

### Step 2: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 3: Install Node Dependencies

```bash
npm install
```

This will install:
- React and React DOM
- React Router (routing)
- Axios (HTTP client)
- Recharts (charting library)
- Tailwind CSS (styling)
- And other dependencies

**Note:** This may take a few minutes depending on your internet connection.

### Step 4: Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

The default values should work for local development:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

### Step 5: Start Frontend Development Server

```bash
npm start
```

The application will automatically open in your browser at http://localhost:3000

If it doesn't open automatically, visit http://localhost:3000 in your browser.

---

## Part 3: Verify Installation

### Test the Application

1. **Visit Homepage** - http://localhost:3000
   - You should see the landing page with features overview

2. **Test Registration**
   - Click "Get Started" or navigate to http://localhost:3000/register
   - Fill in the registration form
   - Submit the form
   - You should be redirected to login page

3. **Test Login**
   - Navigate to http://localhost:3000/login
   - Enter your email and password
   - You should be redirected to dashboard

4. **Test API Documentation**
   - Visit http://localhost:8000/docs
   - Try the `/api/auth/register` endpoint with test data
   - Try the `/api/auth/login` endpoint

### Common Issues and Solutions

#### Backend Issues

**Issue: `ModuleNotFoundError`**
```bash
# Solution: Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Then reinstall dependencies
pip install -r requirements.txt
```

**Issue: `Address already in use`**
```bash
# Solution: Port 8000 is in use, use a different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Issue: Database errors**
```bash
# Solution: Reinitialize database
# Delete the database file
del investment_advisor.db  # Windows
rm investment_advisor.db   # macOS/Linux

# Reinitialize
python -m app.db_init
```

#### Frontend Issues

**Issue: `npm install` fails**
```bash
# Solution: Clear npm cache and retry
npm cache clean --force
npm install
```

**Issue: Port 3000 already in use**
```bash
# Solution: Use a different port
# You'll be prompted to use a different port, type 'Y'
```

**Issue: Cannot connect to API**
```bash
# Solution: Check REACT_APP_API_BASE_URL in .env
# Ensure backend is running on port 8000
# Check browser console for CORS errors
```

---

## Part 4: Development Workflow

### Starting Development

**Terminal 1 - Backend:**
```bash
cd backend
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
# Start backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Stopping Servers

- **Backend**: Press `Ctrl+C` in the backend terminal
- **Frontend**: Press `Ctrl+C` in the frontend terminal

### Making Changes

- **Backend**: Changes are automatically reloaded (thanks to `--reload` flag)
- **Frontend**: Changes are automatically reflected (hot reload)

---

## Part 5: Project Features Status

### ✅ Phase 1 - Completed (Current)

- [x] Project structure setup
- [x] Backend architecture (FastAPI)
- [x] Frontend architecture (React)
- [x] Database models (SQLAlchemy)
- [x] Authentication endpoints (register, login)
- [x] User management endpoints
- [x] Financial profile endpoints
- [x] Modern UI with Tailwind CSS
- [x] Responsive layout
- [x] API service layer
- [x] Authentication context

### 🔄 Phase 2 - Planned

- [ ] JWT authentication middleware
- [ ] Financial profile form implementation
- [ ] Risk profiling engine
- [ ] Portfolio recommendation engine
- [ ] SIP calculator and planner
- [ ] Market data integration (yfinance)
- [ ] Dashboard with real data
- [ ] Charts and visualizations (Recharts)

### 🎯 Phase 3 - Future

- [ ] Machine learning models
- [ ] Advanced portfolio optimization
- [ ] Real-time market data
- [ ] Performance tracking
- [ ] Email notifications
- [ ] Advanced analytics

---

## Part 6: API Testing

### Using FastAPI Docs (Recommended)

1. Visit http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the required fields
5. Click "Execute"

### Using cURL

**Register User:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "phone": "+1234567890"
  }'
```

**Login User:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

---

## Part 7: Database Management

### View Database

**Using DB Browser for SQLite:**
1. Download [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open the `investment_advisor.db` file
3. Browse tables and data

**Using Python:**
```python
import sqlite3

conn = sqlite3.connect('investment_advisor.db')
cursor = conn.cursor()

# View all users
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

conn.close()
```

### Reset Database

```bash
# Delete database
del investment_advisor.db  # Windows
rm investment_advisor.db   # macOS/Linux

# Reinitialize
python -m app.db_init
```

---

## Part 8: Next Steps

### For Development

1. **Implement JWT Middleware**
   - Add authentication dependency to protected routes
   - Extract user from JWT token

2. **Build Financial Profile Form**
   - Create form in frontend
   - Connect to backend API
   - Validate inputs

3. **Implement Risk Profiling**
   - Create questionnaire
   - Calculate risk score
   - Generate recommendations

4. **Integrate Market Data**
   - Use yfinance library
   - Fetch stock data
   - Cache results

### For Production

1. **Security**
   - Use strong SECRET_KEY
   - Enable HTTPS
   - Add rate limiting
   - Implement CSRF protection

2. **Database**
   - Migrate to PostgreSQL
   - Set up backups
   - Add indexes

3. **Deployment**
   - Deploy backend (Heroku, AWS, DigitalOcean)
   - Deploy frontend (Vercel, Netlify)
   - Configure domain and SSL

---

## Support

For issues or questions:
1. Check the README files in backend/ and frontend/ directories
2. Review the API documentation at http://localhost:8000/docs
3. Check the terminal logs for error messages

---

## Summary

You now have a fully functional development environment with:
- ✅ FastAPI backend running on http://localhost:8000
- ✅ React frontend running on http://localhost:3000
- ✅ SQLite database with all tables
- ✅ User authentication (register & login)
- ✅ Modern responsive UI
- ✅ API documentation

**Happy Coding! 🚀**
