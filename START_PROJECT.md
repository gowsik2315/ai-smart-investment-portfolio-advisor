# 🚀 Quick Start Guide

## Running on Another Laptop - Simple Steps

### ✅ What You Need:
1. **Python 3.10+** installed
2. **Node.js 16+** installed
3. This project folder

---

## 📝 Step-by-Step Instructions

### 1️⃣ Open TWO Terminal/PowerShell Windows

You'll need two separate terminal windows - one for backend, one for frontend.

---

### 2️⃣ Terminal Window #1 - Start Backend

```powershell
# Go to backend folder
cd "path\to\AI Smart Investment Portfolio Advisor\backend"

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload
```

**✅ Backend Running:** You should see "Application startup complete"

**Keep this window open!**

---

### 3️⃣ Terminal Window #2 - Start Frontend

```powershell
# Go to frontend folder
cd "path\to\AI Smart Investment Portfolio Advisor\frontend"

# Install dependencies (first time only)
npm install

# Start frontend server
npm start
```

**✅ Frontend Running:** Browser will open automatically to http://localhost:3000

**Keep this window open!**

---

### 4️⃣ Access the Application

**Open your browser and go to:** http://localhost:3000

**First time?**
1. Click "Register" or "Get Started"
2. Create an account
3. Login
4. Start using the app!

---

## 🎯 What Each Server Does:

**Backend (Port 8000):**
- Database operations
- API endpoints
- Business logic
- Data processing

**Frontend (Port 3000):**
- User interface
- Charts and visualizations
- User interactions
- Connects to backend

---

## ⚠️ Important Notes:

### First Time Setup:
- **Backend:** May take 2-5 minutes to install dependencies
- **Frontend:** May take 3-7 minutes to install dependencies
- After first time, startup is instant!

### Both Servers Must Run:
- ❌ Running only backend = No user interface
- ❌ Running only frontend = No data
- ✅ Running both = Full application

### Stopping the Servers:
- Press `Ctrl + C` in each terminal window
- Or close the terminal windows

---

## 🔧 Troubleshooting

### Problem: "Python not found"
**Solution:** Install Python from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

### Problem: "npm not found"
**Solution:** Install Node.js from https://nodejs.org/

### Problem: "Cannot run script"
**Solution:** Run this in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Port 8000 already in use"
**Solution:** 
1. Close any other programs using port 8000
2. Or restart your computer
3. Try again

### Problem: "Port 3000 already in use"
**Solution:** 
- When prompted, press `Y` to use a different port
- Or close other programs using port 3000

### Problem: Database errors
**Solution:**
```powershell
# Delete database file
cd backend
del investment_advisor.db
# Restart backend - it will recreate automatically
```

---

## 📂 Folder Structure Quick Reference

```
AI Smart Investment Portfolio Advisor/
│
├── backend/          ← Start backend from here
│   ├── app/
│   ├── venv/         ← Created after setup
│   ├── requirements.txt
│   └── .env
│
└── frontend/         ← Start frontend from here
    ├── src/
    ├── node_modules/ ← Created after npm install
    └── package.json
```

---

## ✅ Success Checklist

After following the steps, verify:

- [ ] Backend terminal shows "Application startup complete"
- [ ] Frontend terminal shows "Compiled successfully"
- [ ] Browser opens automatically to http://localhost:3000
- [ ] You can see the home page
- [ ] You can register a new account
- [ ] You can login
- [ ] Dashboard loads correctly

---

## 🎉 You're All Set!

If you can access http://localhost:3000 and see the application, **congratulations!** 

Your AI Smart Investment Portfolio Advisor is now running on your new laptop.

---

## 📚 Need More Help?

See **DEPLOYMENT_GUIDE.md** for:
- Detailed troubleshooting
- Advanced configuration
- Production deployment
- Complete technical details

---

**Quick Links:**
- Application: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**Remember:** Both servers must be running for the application to work!

---

**Last Updated:** 2026-07-15
**Version:** 1.0.0
