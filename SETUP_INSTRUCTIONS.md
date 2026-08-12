# AI Smart Investment Portfolio Advisor - Setup Instructions

## 📋 Prerequisites

Before starting, ensure you have the following installed on your system:

1. **Python 3.12+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 18+ and npm** - [Download here](https://nodejs.org/)
3. **Ollama** - [Download here](https://ollama.ai/)
4. **Git** (optional but recommended)

---

## 🚀 Quick Setup Guide

### Step 1: Extract Project

Extract the ZIP file to your desired location:
```
Example: C:\Projects\AI Smart Investment Portfolio Advisor
```

### Step 2: Backend Setup

1. **Open Terminal in Backend Folder**
   ```bash
   cd "AI Smart Investment Portfolio Advisor\backend"
   ```

2. **Create Python Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   
   **Windows (PowerShell):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD):**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **Mac/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**
   
   The `.env` file is already included. **No changes needed** unless you want to customize:
   - Database location
   - JWT secret key
   - Ollama settings

6. **Verify Backend Installation**
   ```bash
   python -c "import fastapi, uvicorn, sqlalchemy; print('✅ Backend dependencies installed successfully!')"
   ```

---

### Step 3: Frontend Setup

1. **Open Terminal in Frontend Folder**
   ```bash
   cd "AI Smart Investment Portfolio Advisor\frontend"
   ```

2. **Install Node Dependencies**
   ```bash
   npm install
   ```
   
   This will install all required packages from `package.json`

3. **Verify Frontend Installation**
   ```bash
   npm list react react-dom
   ```

---

### Step 4: Ollama Setup (AI Service)

1. **Install Ollama** (if not already installed)
   - Download from: https://ollama.ai/
   - Install and run Ollama

2. **Download AI Model**
   
   Open a terminal and run:
   ```bash
   ollama pull qwen2.5:3b
   ```
   
   **Note:** This downloads a 3B parameter model (~2GB). 
   - For better quality (slower): `ollama pull qwen2.5:7b`
   - Current configuration uses: `qwen2.5:3b`

3. **Verify Ollama is Running**
   ```bash
   ollama list
   ```
   
   You should see `qwen2.5:3b` in the list.

4. **Test Ollama API**
   ```bash
   curl http://localhost:11434/api/tags
   ```

---

### Step 5: Generate Dataset (Optional but Recommended)

Generate the synthetic investor dataset for ML training:

```bash
cd backend
python ml/generate_investor_dataset.py
```

**Output:**
- ✅ `backend/datasets/investor_risk_dataset.csv` (50,000 records)
- ✅ `backend/datasets/dataset_report.txt`

---

### Step 6: Run the Project

You need **TWO terminals** - one for backend, one for frontend.

#### Terminal 1 - Backend Server

```bash
cd "AI Smart Investment Portfolio Advisor\backend"

# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1    # Windows PowerShell
# OR
venv\Scripts\activate.bat      # Windows CMD
# OR
source venv/bin/activate       # Mac/Linux

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Backend should start at:** http://127.0.0.1:8000

**Verify backend:**
- Open browser: http://127.0.0.1:8000/docs
- You should see the API documentation

---

#### Terminal 2 - Frontend Server

```bash
cd "AI Smart Investment Portfolio Advisor\frontend"

# Start frontend development server
npm start
```

**Frontend should start at:** http://localhost:3000

**Browser will open automatically** or navigate to: http://localhost:3000

---

## ✅ Verification Checklist

After setup, verify everything is working:

### 1. Backend Health Check
- [ ] Open: http://127.0.0.1:8000/health
- [ ] Should return: `{"status":"healthy","version":"1.0.0"}`

### 2. API Documentation
- [ ] Open: http://127.0.0.1:8000/docs
- [ ] Should see interactive API documentation (Swagger UI)

### 3. Ollama AI Service
- [ ] Open: http://127.0.0.1:8000/api/ollama/health
- [ ] Should return: `{"status":"healthy","model":"qwen2.5:3b",...}`

### 4. Frontend Application
- [ ] Open: http://localhost:3000
- [ ] Should see login/register page

### 5. Database
- [ ] Check file exists: `backend/investment_advisor.db`
- [ ] Backend logs should show: "✅ Database tables created successfully!"

---

## 🧪 Test the Application

### Create Test Account

1. **Register New User**
   - Go to: http://localhost:3000/register
   - Email: `test@example.com`
   - Password: `test123`
   - Full Name: `Test User`

2. **Login**
   - Go to: http://localhost:3000/login
   - Use credentials above

3. **Test Features**
   - ✅ Dashboard
   - ✅ Financial Profile Setup
   - ✅ Risk Assessment
   - ✅ Portfolio Recommendation
   - ✅ Portfolio Analytics
   - ✅ Diversification Analysis
   - ✅ Monte Carlo Simulation
   - ✅ SIP Planner
   - ✅ Stock Explorer

---

## 📂 Project Structure

```
AI Smart Investment Portfolio Advisor/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── ml/               # Machine learning scripts
│   ├── datasets/         # Generated datasets
│   ├── .env              # Environment variables
│   ├── requirements.txt  # Python dependencies
│   └── investment_advisor.db  # SQLite database (created on first run)
│
└── frontend/
    ├── public/           # Static files
    ├── src/
    │   ├── components/   # React components
    │   ├── context/      # React context (auth)
    │   ├── pages/        # Application pages
    │   └── services/     # API service layer
    ├── package.json      # Node dependencies
    └── .env              # Frontend environment variables
```

---

## 🔧 Configuration Files

### Backend `.env` (already configured)

```env
# Application
APP_NAME=Smart Investment Portfolio Advisor
DEBUG=True

# API
API_V1_PREFIX=/api

# Database
DATABASE_URL=sqlite:///./investment_advisor.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Ollama AI
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_TIMEOUT=90
OLLAMA_ENABLED=True
```

### Frontend `.env` (already configured)

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=60000
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" error in backend

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Command not found: npm"

**Solution:**
- Install Node.js from: https://nodejs.org/
- Restart terminal after installation

### Issue: Backend won't start - "Address already in use"

**Solution:**
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

### Issue: Frontend won't start - "Port 3000 already in use"

**Solution:**
```bash
# Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

### Issue: Ollama not responding

**Solution:**
1. Check Ollama is running: `ollama list`
2. Restart Ollama service
3. Pull model again: `ollama pull qwen2.5:3b`
4. Verify: `curl http://localhost:11434/api/tags`

### Issue: AI explanations taking too long

**Solution:**
- Current model: `qwen2.5:3b` (faster, 5-15 seconds)
- If you want better quality (slower):
  ```bash
  ollama pull qwen2.5:7b
  ```
  Then update `backend/.env`:
  ```env
  OLLAMA_MODEL=qwen2.5:7b
  OLLAMA_TIMEOUT=120
  ```

### Issue: Stock data not loading

**Solution:**
1. Verify you're logged in
2. Check internet connection (uses Yahoo Finance API)
3. Try different stocks (US stocks work better: AAPL, MSFT, GOOGL)
4. Yahoo Finance may have rate limits - wait a few minutes and retry

### Issue: Database errors

**Solution:**
```bash
# Delete and recreate database
cd backend
rm investment_advisor.db
# Restart backend server (will recreate database)
```

---

## 🎯 Key Features

### ✅ Implemented Features

1. **User Authentication**
   - Registration & Login
   - JWT-based authentication
   - Session management

2. **Financial Profile Management**
   - Income, expenses, savings tracking
   - Investment goals and time horizon
   - Risk tolerance assessment

3. **Risk Assessment**
   - Automated risk profiling
   - AI-powered risk analysis
   - Personalized recommendations

4. **Portfolio Recommendation**
   - AI-generated asset allocation
   - Custom portfolio strategies
   - Risk-adjusted recommendations

5. **Portfolio Analytics**
   - Performance tracking
   - Returns analysis
   - Risk metrics (Sharpe ratio, volatility, beta)

6. **Diversification Analysis**
   - Sector diversification
   - Asset class analysis
   - Concentration risk assessment

7. **Monte Carlo Simulation**
   - 10,000 simulation runs
   - Probability analysis
   - Future value projections

8. **SIP Calculator**
   - Systematic Investment Plan projections
   - Year-wise growth analysis
   - Goal-based planning

9. **Stock Explorer**
   - Real-time stock data (Yahoo Finance)
   - Historical price charts
   - AI-powered trend analysis

10. **AI-Powered Insights**
    - Risk profile explanations
    - Portfolio recommendations
    - Investment strategies
    - Market trend analysis

---

## 📊 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **SQLite** - Database (easy setup, no installation)
- **Pydantic** - Data validation
- **yfinance** - Stock market data
- **NumPy/Pandas** - Data processing
- **scikit-learn** - Machine learning
- **Ollama** - Local AI inference

### Frontend
- **React 18** - UI framework
- **React Router** - Navigation
- **Recharts** - Data visualization
- **TailwindCSS** - Styling
- **Axios** - HTTP client

---

## 🔐 Security Notes

### Development Mode

⚠️ **This project is configured for DEVELOPMENT:**
- Password hashing is simplified (plain text comparison)
- JWT secret key should be changed for production
- CORS is open for localhost
- Debug mode is enabled

### Production Deployment

Before deploying to production:

1. **Change Secret Key** in `backend/.env`:
   ```env
   SECRET_KEY=<generate-strong-random-key>
   ```

2. **Enable Password Hashing** in `backend/app/core/security.py`:
   - Use bcrypt for password hashing
   - Already imported, just uncomment

3. **Configure CORS** properly in `backend/.env`:
   ```env
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

4. **Use Production Database**:
   - Switch from SQLite to PostgreSQL/MySQL
   - Update `DATABASE_URL` in `.env`

5. **Disable Debug Mode**:
   ```env
   DEBUG=False
   ```

6. **Use Production Build** for frontend:
   ```bash
   cd frontend
   npm run build
   ```

---

## 📞 Support

### Common Commands Reference

```bash
# Backend
cd backend
.\venv\Scripts\Activate.ps1                    # Activate venv (Windows)
source venv/bin/activate                       # Activate venv (Mac/Linux)
pip install -r requirements.txt                # Install dependencies
uvicorn app.main:app --reload                  # Start server
python ml/generate_investor_dataset.py         # Generate dataset

# Frontend
cd frontend
npm install                                    # Install dependencies
npm start                                      # Start dev server
npm run build                                  # Production build

# Ollama
ollama list                                    # List installed models
ollama pull qwen2.5:3b                        # Download model
ollama serve                                   # Start Ollama service
```

---

## ✨ Additional Resources

- **API Documentation**: http://127.0.0.1:8000/docs (when backend is running)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Ollama Docs**: https://ollama.ai/
- **TailwindCSS**: https://tailwindcss.com/

---

## 🎉 You're All Set!

If you've completed all steps successfully:

1. ✅ Backend running at: http://127.0.0.1:8000
2. ✅ Frontend running at: http://localhost:3000
3. ✅ Ollama running at: http://localhost:11434
4. ✅ Database created: `backend/investment_advisor.db`
5. ✅ Dataset generated: `backend/datasets/investor_risk_dataset.csv`

**Start using the application:**
- Register a new account
- Set up your financial profile
- Get AI-powered investment recommendations
- Track your portfolio performance
- Explore advanced analytics

---

**Project Version:** 1.0.0  
**Last Updated:** 2026-08-07  
**Setup Time:** ~15-20 minutes

**Enjoy your AI-powered investment advisor! 🚀💰📊**
