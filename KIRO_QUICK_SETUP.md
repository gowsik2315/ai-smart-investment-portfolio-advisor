# 🚀 Kiro Quick Setup - AI Smart Investment Portfolio Advisor

## Quick Setup Prompt for Kiro

Copy and paste this prompt into Kiro after extracting the ZIP:

---

```
I have extracted the "AI Smart Investment Portfolio Advisor" project. Please set it up and run it on my system.

PROJECT LOCATION: [paste your extracted folder path here]

SETUP REQUIREMENTS:
1. Backend: Python 3.12+ with FastAPI
2. Frontend: Node.js 18+ with React
3. AI Service: Ollama with qwen2.5:3b model
4. Database: SQLite (auto-created)

TASKS TO COMPLETE:
1. Setup Backend:
   - Create Python virtual environment in backend/
   - Install dependencies from backend/requirements.txt
   - Verify .env file exists (already included)
   - Generate synthetic dataset using backend/ml/generate_investor_dataset.py

2. Setup Frontend:
   - Install npm dependencies from frontend/package.json
   - Verify .env file exists (already included)

3. Setup Ollama:
   - Check if Ollama is installed and running
   - Pull model: ollama pull qwen2.5:3b
   - Verify Ollama API at http://localhost:11434

4. Start Project:
   - Run backend: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   - Run frontend: npm start
   - Verify both servers are running

5. Test Application:
   - Backend: http://127.0.0.1:8000/docs
   - Frontend: http://localhost:3000
   - Create test account and verify all features work

EXPECTED OUTPUTS:
✅ Backend running at http://127.0.0.1:8000
✅ Frontend running at http://localhost:3000
✅ Ollama running at http://localhost:11434
✅ Database created: backend/investment_advisor.db
✅ Dataset generated: backend/datasets/investor_risk_dataset.csv (50,000 records)

NOTES:
- All configuration files (.env) are already included
- No manual configuration needed unless customizing
- SQLite database auto-creates on first backend run
- Project uses qwen2.5:3b model (faster, 2GB download)

If any issues occur, refer to SETUP_INSTRUCTIONS.md for detailed troubleshooting.
```

---

## Alternative: Step-by-Step Kiro Commands

If the above prompt doesn't work, use these individual commands:

### Step 1: Navigate to Project
```
cd "AI Smart Investment Portfolio Advisor"
```

### Step 2: Backend Setup
```
Create Python virtual environment in backend folder, install requirements.txt, and verify the .env file exists
```

### Step 3: Generate Dataset
```
Run the Python script backend/ml/generate_investor_dataset.py to generate the synthetic investor dataset
```

### Step 4: Frontend Setup
```
Install npm dependencies in frontend folder using package.json
```

### Step 5: Check Ollama
```
Verify Ollama is installed and pull the qwen2.5:3b model
```

### Step 6: Start Servers
```
Start the backend server using uvicorn on port 8000 and the frontend using npm start
```

### Step 7: Verify
```
Open backend API docs at http://127.0.0.1:8000/docs and frontend at http://localhost:3000
```

---

## 📋 Pre-Setup Checklist

Before sending to Kiro, ensure the ZIP contains:

- ✅ `backend/` folder with all Python code
- ✅ `frontend/` folder with all React code
- ✅ `backend/.env` file (configuration)
- ✅ `frontend/.env` file (configuration)
- ✅ `backend/requirements.txt` (Python dependencies)
- ✅ `frontend/package.json` (Node dependencies)
- ✅ `backend/ml/generate_investor_dataset.py` (dataset generator)
- ✅ `SETUP_INSTRUCTIONS.md` (detailed guide)
- ✅ `KIRO_QUICK_SETUP.md` (this file)

**EXCLUDE from ZIP:**
- ❌ `backend/venv/` (virtual environment - will be recreated)
- ❌ `frontend/node_modules/` (npm packages - will be reinstalled)
- ❌ `backend/investment_advisor.db` (database - will be auto-created)
- ❌ `backend/__pycache__/` and `frontend/.cache/` (cache files)
- ❌ `.git/` folder (if present)

---

## 🎯 Expected Setup Time

- **Automatic (Kiro)**: 5-10 minutes
- **Manual**: 15-20 minutes

---

## 🔍 Verification Commands for Kiro

After setup, ask Kiro to run:

```
Check if the backend server is running at http://127.0.0.1:8000/health
Check if the frontend server is running at http://localhost:3000
Check if Ollama is running at http://localhost:11434/api/tags
Check if the database file exists at backend/investment_advisor.db
Check if the dataset file exists at backend/datasets/investor_risk_dataset.csv with 50,000 records
```

---

## 📞 Troubleshooting Commands for Kiro

If setup fails, ask Kiro to:

```
Show me the error logs from the backend server
Show me the error logs from the frontend compilation
Check if Python virtual environment is activated in backend
Check if Node.js and npm are installed
Check if Ollama is installed and running
List all Python packages installed in backend/venv
List all npm packages installed in frontend/node_modules
```

---

**That's it! Your project is ready to be set up on any Kiro instance.** 🎉
