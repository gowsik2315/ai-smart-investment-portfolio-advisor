# 🚀 Deployment Guide - AI Smart Investment Portfolio Advisor

## How to Run This Project on Another Laptop

This guide will help you set up and run the complete project on a new machine.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software:
1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **Node.js 16 or higher**
   - Download from: https://nodejs.org/ (LTS version recommended)
   - This includes npm
   - Verify: `node --version` and `npm --version`

3. **Git** (optional, for cloning)
   - Download from: https://git-scm.com/downloads

---

## 📁 Step 1: Transfer Project Files

### Option A: Using Git (Recommended)
```bash
# If you've pushed to a repository
git clone <your-repository-url>
cd "AI Smart Investment Portfolio Advisor"
```

### Option B: Manual Transfer
1. Copy the entire project folder to the new laptop
2. You can use:
   - USB drive
   - Cloud storage (Google Drive, OneDrive, etc.)
   - Network share
   - Email (if size permits)

### Option C: Zip and Transfer
1. On current laptop:
   - Right-click the project folder
   - Select "Send to" → "Compressed (zipped) folder"
   - Transfer the zip file

2. On new laptop:
   - Extract the zip file
   - Open the extracted folder

---

## 🐍 Step 2: Backend Setup

### 2.1 Navigate to Backend Folder
```bash
cd "AI Smart Investment Portfolio Advisor/backend"
```

### 2.2 Create Virtual Environment
```bash
# Windows
python -m venv venv

# Or if python3 is the command
python3 -m venv venv
```

### 2.3 Activate Virtual Environment
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
.\venv\Scripts\activate.bat

# If you get execution policy error in PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
```

### 2.4 Install Python Dependencies
```bash
# Make sure virtual environment is activated (you should see (venv) in prompt)
pip install --upgrade pip
pip install -r requirements.txt
```

**This will install:**
- FastAPI (web framework)
- SQLAlchemy (database)
- Pandas, NumPy (data processing)
- yfinance (stock data)
- All other dependencies

**Installation time:** ~2-5 minutes depending on internet speed

### 2.5 Verify Backend Installation
```bash
python -c "import fastapi, sqlalchemy, pandas, numpy, yfinance; print('✓ All packages installed successfully!')"
```

---

## 📦 Step 3: Frontend Setup

### 3.1 Navigate to Frontend Folder
```bash
# From project root
cd frontend

# Or from backend folder
cd ../frontend
```

### 3.2 Install Node Dependencies
```bash
npm install
```

**This will install:**
- React and React Router
- Axios (HTTP client)
- Recharts (charting library)
- TailwindCSS (styling)
- All other frontend dependencies

**Installation time:** ~3-7 minutes depending on internet speed

### 3.3 Verify Frontend Installation
```bash
npm list react recharts axios
```

---

## 🔧 Step 4: Configuration

### 4.1 Backend Configuration

**Check `.env` file exists:**
```bash
# In backend folder
ls .env
# Or on Windows Command Prompt
dir .env
```

**If `.env` file doesn't exist, create it:**
```bash
# Copy from example
copy .env.example .env
# Or on PowerShell
Copy-Item .env.example .env
```

**Default `.env` contents:**
```env
# Application Settings
APP_NAME="Smart Investment Portfolio Advisor"
APP_VERSION="1.0.0"
DEBUG=True

# API Settings
API_V1_PREFIX="/api"
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database
DATABASE_URL=sqlite:///./investment_advisor.db

# Security (Generate new secret key for production!)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

**⚠️ Important:** For production, generate a new SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.2 Frontend Configuration

Frontend is pre-configured to connect to `http://localhost:8000`

If you need to change the backend URL, edit:
- `frontend/src/services/*.js` files
- Look for `API_BASE_URL` and update if needed

---

## 🚀 Step 5: Run the Application

### 5.1 Start Backend Server

**Open Terminal/PowerShell #1:**
```bash
# Navigate to backend folder
cd "AI Smart Investment Portfolio Advisor/backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start backend server
uvicorn app.main:app --reload
```

**Expected output:**
```
🚀 Starting application...
📊 Creating database tables...
✅ Database tables created successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Backend is now running on:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs

### 5.2 Start Frontend Server

**Open Terminal/PowerShell #2 (separate window):**
```bash
# Navigate to frontend folder
cd "AI Smart Investment Portfolio Advisor/frontend"

# Start frontend server
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view smart-investment-advisor-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Frontend is now running on:** http://localhost:3000

---

## 🌐 Step 6: Access the Application

1. **Open your browser**
2. **Navigate to:** http://localhost:3000
3. **You should see the home page**

### First Time Setup:
1. Click "Get Started" or "Register"
2. Create a new account
3. Login with your credentials
4. Start using the application!

---

## 📊 Step 7: Verify All Modules

### Available Features:
1. **Dashboard** - http://localhost:3000/dashboard
2. **Financial Profile** - http://localhost:3000/profile
3. **Risk Assessment** - http://localhost:3000/risk-assessment
4. **Portfolio Recommendation** - http://localhost:3000/portfolio-recommendation
5. **Portfolio Analytics** - http://localhost:3000/portfolio-analytics
6. **Diversification Analysis** - http://localhost:3000/diversification
7. **Monte Carlo Simulation** - http://localhost:3000/monte-carlo
8. **SIP Planner** - http://localhost:3000/sip-planner
9. **Stock Explorer** - http://localhost:3000/stocks

### Test Each Module:
✅ Create a financial profile
✅ Take risk assessment
✅ Generate portfolio recommendations
✅ Run portfolio analytics
✅ Analyze diversification
✅ Run Monte Carlo simulation
✅ Plan SIP investments
✅ Search for stocks

---

## 🛠️ Troubleshooting

### Issue 1: "python not recognized"
**Solution:**
- Ensure Python is installed
- Add Python to PATH
- Restart terminal after installation

### Issue 2: "venv activation fails on Windows"
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: "pip install fails"
**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### Issue 4: "npm install fails"
**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Install again
npm install
```

### Issue 5: "Port 8000 already in use"
**Solution:**
```bash
# Find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Then restart backend
```

### Issue 6: "Port 3000 already in use"
**Solution:**
```bash
# The prompt will ask if you want to use another port
# Type 'y' and press Enter
# Or kill the process using port 3000
```

### Issue 7: "Database errors"
**Solution:**
```bash
# Delete the database file and restart
# In backend folder:
del investment_advisor.db
# Then restart backend - it will recreate tables
```

### Issue 8: "CORS errors in browser"
**Solution:**
- Check that backend is running on port 8000
- Check frontend is running on port 3000
- Verify `.env` file has correct ALLOWED_ORIGINS

### Issue 9: "Module not found errors"
**Solution:**
```bash
# Backend:
pip install -r requirements.txt --force-reinstall

# Frontend:
npm install
```

---

## 📝 Development Tips

### Running in Development Mode:

**Backend with auto-reload:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend with specific port:**
```bash
PORT=3001 npm start
```

### Accessing from Another Device on Same Network:

**Backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Access from: `http://<your-ip>:8000`

**Frontend:**
Update `API_BASE_URL` in frontend services to use your IP instead of localhost

---

## 🔒 Production Deployment (Optional)

For production deployment:

### Backend:
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend:
```bash
# Build production bundle
npm run build

# Serve with static server
npm install -g serve
serve -s build -l 3000
```

### Environment:
- Set `DEBUG=False` in `.env`
- Generate secure `SECRET_KEY`
- Use PostgreSQL instead of SQLite for production
- Set up HTTPS/SSL certificates
- Configure proper CORS origins

---

## 📦 Project Structure

```
AI Smart Investment Portfolio Advisor/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # Application entry
│   ├── venv/             # Virtual environment
│   ├── .env              # Environment variables
│   ├── requirements.txt  # Python dependencies
│   └── investment_advisor.db  # SQLite database
│
├── frontend/
│   ├── public/           # Static files
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   ├── context/      # React context
│   │   └── App.js        # Main app component
│   ├── node_modules/     # Node dependencies
│   ├── package.json      # Node dependencies list
│   └── tailwind.config.js
│
└── Documentation files (.md)
```

---

## ✅ Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 16+ installed
- [ ] Project files copied to new laptop
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] `.env` file exists in backend folder
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Application accessible at http://localhost:3000
- [ ] All modules working correctly

---

## 🆘 Need Help?

1. **Check terminal output** for error messages
2. **Verify both servers are running** (backend on 8000, frontend on 3000)
3. **Check browser console** (F12) for frontend errors
4. **Review logs** in terminal windows
5. **Ensure all dependencies installed** correctly

---

## 🎉 Success!

If you can access http://localhost:3000 and see the application, you're all set!

**Enjoy using your AI Smart Investment Portfolio Advisor!** 🚀📈💰

---

**Last Updated:** 2026-07-15
**Version:** 1.0.0
**Status:** Production Ready
