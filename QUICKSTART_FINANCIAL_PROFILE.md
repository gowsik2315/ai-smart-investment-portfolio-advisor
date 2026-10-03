# Quick Start Guide - Financial Profile Module

This guide will help you get the Financial Profile module up and running in minutes.

## Prerequisites

- Python 3.8+ installed
- Node.js 14+ and npm installed
- Git (optional)

## Step 1: Backend Setup (5 minutes)

### 1.1 Navigate to backend directory
```bash
cd backend
```

### 1.2 Activate virtual environment (if not already active)

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 1.3 Install dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### 1.4 Run database test
```bash
python test_financial_profile.py
```

You should see:
```
🎉 All tests PASSED! Financial Profile module is ready.
```

### 1.5 Start the backend server
```bash
python -m uvicorn app.main:app --reload
```

Server will start at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Step 2: Frontend Setup (3 minutes)

### 2.1 Open a new terminal and navigate to frontend directory
```bash
cd frontend
```

### 2.2 Install dependencies (if not already installed)
```bash
npm install
```

### 2.3 Start the frontend server
```bash
npm start
```

Frontend will start at: `http://localhost:3000`

## Step 3: Test the Module (5 minutes)

### 3.1 Register a New User
1. Open browser: `http://localhost:3000`
2. Click "Register" or go to `http://localhost:3000/register`
3. Fill in the registration form:
   - Email: `demo@example.com`
   - Password: `password123`
   - Full Name: `Demo User`
   - Phone: `9876543210` (optional)
4. Click "Register"

### 3.2 Login
1. Go to `http://localhost:3000/login`
2. Enter credentials:
   - Email: `demo@example.com`
   - Password: `password123`
3. Click "Login"

### 3.3 Create Financial Profile
1. Navigate to `http://localhost:3000/profile` or click "Profile" in navigation
2. Fill in the form:
   - **Age:** `30`
   - **Monthly Income:** `75000`
   - **Monthly Savings:** `25000`
   - **Investment Horizon:** `5-10 Years`
   - **Risk Tolerance:** `Medium - Can accept moderate fluctuations`
   - **Financial Goal:** `Wealth Creation`
3. Watch the **Financial Summary** section update automatically
4. Click "Create Profile"
5. You should see: "Financial profile created successfully!"
6. You'll be redirected to the dashboard

### 3.4 Update Financial Profile
1. Go back to `http://localhost:3000/profile`
2. Notice your profile is loaded automatically
3. Change any field (e.g., Risk Tolerance to `High`)
4. Click "Update Profile"
5. You should see: "Financial profile updated successfully!"

## Step 4: Verify with API (Optional)

### 4.1 Get your access token
After logging in, check browser's localStorage:
- Open Developer Tools (F12)
- Go to "Application" or "Storage" tab
- Find "localStorage"
- Copy the value of `access_token`

### 4.2 Test API with cURL

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Update Profile:**
```bash
curl -X PUT http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"monthly_savings": 30000}'
```

### 4.3 Or use Swagger UI
1. Go to `http://localhost:8000/docs`
2. Click "Authorize" button (top right)
3. Enter: `Bearer YOUR_TOKEN_HERE`
4. Click "Authorize"
5. Now you can test all endpoints directly

## Understanding the Financial Summary

When you fill in Monthly Income and Monthly Savings, you'll see:

```
┌─────────────────────────────────────────┐
│       Financial Summary                  │
├─────────────────────────────────────────┤
│ Savings Rate:      33.3%                │  (25000 / 75000 * 100)
│ Annual Savings:    ₹3,00,000            │  (25000 * 12)
│ Monthly Expenses:  ₹50,000              │  (75000 - 25000)
│ Expense Ratio:     66.7%                │  (50000 / 75000 * 100)
└─────────────────────────────────────────┘
```

## Troubleshooting

### Backend Issues

**Issue:** `ModuleNotFoundError: No module named 'jose'`
```bash
pip install python-jose[cryptography]
```

**Issue:** `Database is locked`
```bash
# Close any open database connections
# Delete investment_advisor.db and run again
```

**Issue:** Port 8000 already in use
```bash
# Change port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**Issue:** `Cannot connect to backend`
- Check if backend is running on port 8000
- Check `.env` file: `REACT_APP_API_BASE_URL=http://localhost:8000`

**Issue:** `Module not found` errors
```bash
rm -rf node_modules package-lock.json
npm install
```

**Issue:** Port 3000 already in use
```bash
# The terminal will ask if you want to use a different port
# Type 'y' and press Enter
```

## What's Next?

Now that your Financial Profile module is working, you can:

1. **Explore the API Documentation**
   - Visit `http://localhost:8000/docs`
   - Try different endpoints

2. **Check the Module Documentation**
   - Read `FINANCIAL_PROFILE_MODULE.md` for detailed API specs

3. **Customize the Form**
   - Edit `frontend/src/pages/FinancialProfile.js`
   - Add new fields or validation rules

4. **Integrate with Dashboard**
   - Display profile summary in the dashboard
   - Show investment recommendations based on profile

## Key Files to Know

### Backend
- `backend/app/api/profile.py` - API endpoints
- `backend/app/models/financial_profile.py` - Database model
- `backend/app/schemas/financial_profile.py` - Validation schemas
- `backend/app/core/security.py` - JWT authentication

### Frontend
- `frontend/src/pages/FinancialProfile.js` - Profile form
- `frontend/src/services/profileService.js` - API client
- `frontend/src/components/common/Select.js` - Select component

## Getting Help

- **API Documentation:** `http://localhost:8000/docs`
- **Module Documentation:** `FINANCIAL_PROFILE_MODULE.md`
- **Backend Logs:** Check terminal where backend is running
- **Frontend Logs:** Check browser console (F12)

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] User registration working
- [ ] User login working
- [ ] Profile creation working
- [ ] Profile retrieval working
- [ ] Profile update working
- [ ] Financial summary displaying correctly
- [ ] Form validation working
- [ ] JWT authentication working

---

**Congratulations! 🎉** Your Financial Profile module is now fully functional!
