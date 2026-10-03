# Setup & Verification Guide

## Financial Profile Module - Complete Setup Instructions

### Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.8 or higher
- [ ] Node.js 14 or higher
- [ ] npm (comes with Node.js)
- [ ] Virtual environment (venv) support

## Backend Setup

### Step 1: Virtual Environment Setup

Navigate to the backend directory and create/activate virtual environment:

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI - Web framework
- SQLAlchemy - Database ORM
- python-jose - JWT authentication
- uvicorn - ASGI server
- And other required packages

### Step 3: Verify Installation

```bash
pip list | grep -E "(fastapi|sqlalchemy|jose|uvicorn)"
```

Expected output should show:
```
fastapi              0.109.0
sqlalchemy           2.0.25
python-jose          3.3.0
uvicorn              0.27.0
```

### Step 4: Initialize Database

```bash
python app/db_init.py
```

Or simply start the server (it will create tables automatically):

```bash
python -m uvicorn app.main:app --reload
```

### Step 5: Run Tests

```bash
python test_financial_profile.py
```

Expected output:
```
🧪 FINANCIAL PROFILE MODULE TEST SUITE
============================================================
Testing Financial Profile Database Setup
============================================================

1. Creating database tables...
   ✓ Tables created successfully

2. Checking tables...
   ✓ Table 'users' exists
   ✓ Table 'financial_profiles' exists

...

🎉 All tests PASSED! Financial Profile module is ready.
```

### Step 6: Access API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup

### Step 1: Install Dependencies

Open a new terminal:

```bash
cd frontend
npm install
```

### Step 2: Configure Environment

Check if `.env` file exists with correct settings:

```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

### Step 3: Start Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

### Step 4: Verify Frontend

Open browser and check:
- [ ] Home page loads
- [ ] Can navigate to `/register`
- [ ] Can navigate to `/login`
- [ ] Can navigate to `/profile` (will redirect if not logged in)

## Verification Checklist

### Backend Verification

```bash
# In backend directory with activated venv
python -c "from app.models.financial_profile import FinancialProfile; print('✓ Model import successful')"
python -c "from app.schemas.financial_profile import FinancialProfileCreate; print('✓ Schema import successful')"
python -c "from app.api.profile import router; print('✓ Router import successful')"
python -c "from app.core.security import get_current_user_id; print('✓ Security import successful')"
```

All should print `✓ [Component] import successful`

### Database Verification

```bash
# Check if database file exists
ls -la investment_advisor.db

# Run test script
python test_financial_profile.py
```

### API Verification

With server running (`python -m uvicorn app.main:app --reload`):

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}

# Test root endpoint
curl http://localhost:8000/

# Expected response:
# {"message":"Welcome to Smart Investment Portfolio Advisor API","version":"1.0.0","status":"running","docs":"/docs"}
```

### Authentication Flow Test

1. **Register User:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "phone": "1234567890"
  }'
```

2. **Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

3. **Create Financial Profile:**
```bash
curl -X POST http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "monthly_income": 75000,
    "monthly_savings": 25000,
    "investment_horizon": "5-10 Years",
    "risk_tolerance": "Medium",
    "financial_goal": "Wealth Creation"
  }'
```

4. **Get Financial Profile:**
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

5. **Update Financial Profile:**
```bash
curl -X PUT http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_savings": 30000,
    "risk_tolerance": "High"
  }'
```

## Common Issues & Solutions

### Issue 1: Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: Database Locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Close all connections to the database
# Stop the server
# Delete the database file
rm investment_advisor.db

# Restart the server (it will recreate the database)
python -m uvicorn app.main:app --reload
```

### Issue 3: Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Use a different port
python -m uvicorn app.main:app --reload --port 8001

# Or find and kill the process using the port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

### Issue 4: CORS Errors in Frontend

**Error in browser console:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution:**
Check `backend/app/main.py` has CORS middleware configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 5: JWT Token Errors

**Error:**
```
401 Unauthorized: Not authenticated
```

**Solution:**
1. Check token is being sent in header: `Authorization: Bearer <token>`
2. Check token hasn't expired (default: 30 minutes)
3. Login again to get a fresh token
4. Check localStorage has the token saved

### Issue 6: Frontend Not Loading

**Error:**
```
Cannot GET /
```

**Solution:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## Environment Configuration

### Backend `.env`

Create `backend/.env`:
```env
# Application
APP_NAME=Smart Investment Portfolio Advisor
APP_VERSION=1.0.0
DEBUG=True

# Database
DATABASE_URL=sqlite:///./investment_advisor.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# API
API_V1_PREFIX=/api
```

### Frontend `.env`

Create `frontend/.env`:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

## Performance Check

### Backend Performance

```bash
# Check server startup time
time python -m uvicorn app.main:app

# Should start in < 5 seconds
```

### API Response Time

```bash
# Install httpie (optional)
pip install httpie

# Test response time
time http GET http://localhost:8000/health

# Should respond in < 100ms
```

## Security Checklist

- [ ] `.env` files are in `.gitignore`
- [ ] Database file is in `.gitignore`
- [ ] JWT secret is not hardcoded (using environment variable)
- [ ] Passwords are hashed (currently disabled for development)
- [ ] CORS is configured properly
- [ ] Input validation is working (via Pydantic)
- [ ] SQL injection protection (via SQLAlchemy ORM)

## Production Readiness Checklist

Before deploying to production:

- [ ] Enable password hashing in `app/core/security.py`
- [ ] Change SECRET_KEY to a strong random value
- [ ] Set DEBUG=False in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Add rate limiting
- [ ] Add request logging
- [ ] Set up HTTPS
- [ ] Configure proper CORS origins
- [ ] Add input sanitization
- [ ] Set up monitoring and alerts
- [ ] Add database backups
- [ ] Review and update dependencies

## Next Steps

After successful setup and verification:

1. ✅ Test user registration
2. ✅ Test user login
3. ✅ Test profile creation
4. ✅ Test profile retrieval
5. ✅ Test profile updates
6. ✅ Test form validation
7. ✅ Review API documentation at `/docs`
8. ✅ Check financial summary calculations
9. ✅ Test error handling
10. ✅ Review the codebase

## Support Resources

- **API Documentation:** `http://localhost:8000/docs`
- **Module Documentation:** `FINANCIAL_PROFILE_MODULE.md`
- **Quick Start Guide:** `QUICKSTART_FINANCIAL_PROFILE.md`
- **Architecture:** `ARCHITECTURE.md`

## Verification Complete!

Once all checks pass, your Financial Profile module is ready for development and testing.

For production deployment, follow the Production Readiness Checklist above.
