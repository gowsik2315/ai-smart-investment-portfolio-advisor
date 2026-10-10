# Testing Guide

Covers the automated suite and the manual walkthroughs for registration
and login.

---

## Automated tests

```bash
cd backend
pytest                              # 288 tests
pytest tests/test_security.py -v    # one module, verbose
pytest -k volatility                # by keyword
```

No network access is required: price data is synthesised by the fixtures
in `tests/conftest.py`, because `yfinance` is rate-limited and would make
the suite flaky for reasons unrelated to the code.

| Module | What it covers |
|---|---|
| `test_monte_carlo_simulator.py` | GBM maths, closed-form drift preservation, path positivity at extreme sigma, VaR/CVaR ordering, seed reproducibility, input validation |
| `test_ml_features.py` | Feature construction, and the leakage guards: a feature row must not change when future data is removed, and the target must equal independently-computed forward volatility |
| `test_ml_registry_and_service.py` | Artifact contract (a mismatched or reordered feature set must be refused), and the volatility fallback chain |
| `test_ml_evaluation.py` | RMSE/MAE/QLIKE, including QLIKE's asymmetry, plus the naive and HAR baselines |
| `test_ml_trend.py` | The stock-trend module: label correctness and leakage, the descriptive trend signals, base rate, range maths against the closed form, Brier-skill scoring, the classifier artifact contract (including refusing a volatility artifact), and the service fallbacks |
| `test_ml_explain.py` | The Stock Predictor's AI explanation: the prompt's wording rules per situation, the output guard (advice, certainty, negated disclaimers, the appended base-rate caveat), and the endpoint's caching and failure behaviour with Ollama stubbed |
| `test_ml_data.py` | Ticker validation: hostile symbols such as drive-letter paths are rejected before they can reach a cache filename |
| `test_security.py` | bcrypt hashing, the 72-byte input limit measured in bytes, JWT round-trips, forged-token rejection |

### The tests worth understanding

Two carry more weight than the rest:

- **`test_feature_row_unchanged_when_future_is_removed`** — a volatility
  model that peeks at the future scores beautifully offline and is
  worthless live, and no metric reveals it. Only this test does.
- **`test_embargo_counts_dates_not_rows_on_a_panel`** — a regression
  test for a leak invisible on single-ticker data. With 10 tickers there
  are 10 rows per date, so an embargo measured in rows collapsed to one
  trading day instead of 21.

### Note on bcrypt's password limit

bcrypt accepts at most 72 **bytes**. The registration schema once allowed
100 **characters**, so a long passphrase reached bcrypt, raised, and
surfaced as an unhandled 500. Validation now measures UTF-8 bytes at both
the schema and the hasher, so over-long passwords get a 422. Truncating
instead would be worse — two passwords sharing a 72-byte prefix would
hash identically.

---

## Manual testing

Register an account at http://localhost:3000/register. Each analytics
page has a **Generate Sample Data** button to populate it.

Note that every data endpoint requires a JWT. If pages redirect you to
login, the token (stored as `access_token`) is missing or expired.

---

## 🎯 How to Test Registration

### Step 1: Open the Application
Open your browser and go to: **http://localhost:3000**

### Step 2: Navigate to Registration
Click **"Get Started"** or **"Register"** button

### Step 3: Fill in the Form

**Required Fields:**
- **Full Name:** Your Name (minimum 2 characters)
- **Email:** your@email.com (valid email format)
- **Password:** 8-72 characters
- **Confirm Password:** Must match password

**Optional Field:**
- **Phone:** Your phone number

### Step 4: Submit
Click **"Create Account"**

### Step 5: Verify Success
- You should be redirected to the login page
- You should see a success message (if implemented)
- No errors in browser console

---

## 🧪 Test Cases

### Test Case 1: Valid Registration ✅
```
Full Name: John Doe
Email: john@example.com
Phone: +1234567890
Password: password123
Confirm Password: password123

Expected: Success → Redirect to login
```

### Test Case 2: Email Already Exists ⚠️
```
Register with same email twice

Expected: Error message "Email already registered"
```

### Test Case 3: Password Mismatch ⚠️
```
Password: password123
Confirm Password: password456

Expected: Error message "Passwords do not match"
```

### Test Case 4: Short Password ⚠️
```
Password: short

Expected: Error message "Password must be at least 8 characters"
```

### Test Case 5: Invalid Email ⚠️
```
Email: notanemail

Expected: Browser validation or error message
```

### Test Case 6: Long Password (Edge Case) ✅
```
Password: 72 characters exactly

Expected: Success
```

### Test Case 7: Too Long Password ⚠️
```
Password: More than 72 characters

Expected: Error message "Password must be 72 characters or less"
```

---

## 🔐 Test Login

### Step 1: Navigate to Login
Go to: **http://localhost:3000/login**

### Step 2: Enter Credentials
```
Email: john@example.com
Password: password123
```

### Step 3: Submit
Click **"Sign In"**

### Step 4: Verify Success
- Should redirect to: **http://localhost:3000/dashboard**
- Token should be stored in localStorage
- Navbar should show "Logout" button

---

## 🔌 Test API Directly

### Using API Documentation

1. Go to: **http://localhost:8000/docs**

2. **Test Registration Endpoint:**
   - Click on `POST /api/auth/register`
   - Click "Try it out"
   - Enter test data:
   ```json
   {
     "email": "test@example.com",
     "password": "testpass123",
     "full_name": "Test User",
     "phone": "+1234567890"
   }
   ```
   - Click "Execute"
   - Check response (should be 201 Created)

3. **Test Login Endpoint:**
   - Click on `POST /api/auth/login`
   - Click "Try it out"
   - Enter credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "testpass123"
   }
   ```
   - Click "Execute"
   - Check response (should return access_token and refresh_token)

### Using cURL

**Register User:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"curl@test.com\",\"password\":\"curltest123\",\"full_name\":\"Curl Test\",\"phone\":\"+1234567890\"}"
```

**Login User:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"curl@test.com\",\"password\":\"curltest123\"}"
```

### Using PowerShell

**Register User:**
```powershell
$body = @{
    email = "ps@test.com"
    password = "pstest123"
    full_name = "PowerShell Test"
    phone = "+1234567890"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

**Login User:**
```powershell
$body = @{
    email = "ps@test.com"
    password = "pstest123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

---

## 📊 Verify Database

### Check if User Was Created

**Option 1: Using Python**
```python
import sqlite3

conn = sqlite3.connect('backend/investment_advisor.db')
cursor = conn.cursor()

cursor.execute("SELECT id, email, full_name, created_at FROM users")
users = cursor.fetchall()

for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Name: {user[2]}, Created: {user[3]}")

conn.close()
```

**Option 2: Using DB Browser for SQLite**
1. Download DB Browser: https://sqlitebrowser.org/
2. Open `backend/investment_advisor.db`
3. Go to "Browse Data" tab
4. Select "users" table
5. View registered users

---

## 🔍 Debugging Tips

### Check Backend Logs
Look at the terminal running the backend server for any errors.

### Check Frontend Console
Open browser DevTools (F12) → Console tab
Look for any JavaScript errors or failed API calls.

### Check Network Tab
Open browser DevTools (F12) → Network tab
Watch the API calls when you submit the form:
- Should see POST request to `/api/auth/register`
- Check the request payload
- Check the response status (should be 201 or 200)

### Common Issues

**Issue 1: CORS Error**
```
Error: CORS policy blocked
```
**Solution:** Backend CORS is configured for localhost:3000 and localhost:3001

**Issue 2: Network Error**
```
Error: Network Error
```
**Solution:** Make sure backend server is running on port 8000

**Issue 3: 400 Bad Request**
**Solution:** Check request body format, make sure all required fields are present

**Issue 4: 500 Internal Server Error**
**Solution:** Check backend terminal for detailed error message

---

## ✅ Expected Behavior

### Successful Registration Flow

1. **User fills form** → All validation passes
2. **Frontend sends POST request** → To `/api/auth/register`
3. **Backend validates data** → Using Pydantic schemas
4. **Backend checks email** → Not already registered
5. **Backend hashes password** → Using bcrypt (max 72 chars)
6. **Backend creates user** → Inserts into database
7. **Backend returns success** → 201 Created with user data
8. **Frontend redirects** → To login page
9. **User can login** → Using registered credentials

### Successful Login Flow

1. **User enters credentials** → Email and password
2. **Frontend sends POST request** → To `/api/auth/login`
3. **Backend finds user** → By email
4. **Backend verifies password** → Using bcrypt
5. **Backend generates tokens** → JWT access & refresh tokens
6. **Backend returns tokens** → To frontend
7. **Frontend stores tokens** → In localStorage
8. **Frontend updates context** → User is authenticated
9. **Frontend redirects** → To dashboard

---

## 🎯 Testing Checklist

- [ ] Register new user with valid data
- [ ] Try to register with same email (should fail)
- [ ] Login with registered credentials
- [ ] Check user appears in database
- [ ] Test password validation (too short)
- [ ] Test password validation (too long)
- [ ] Test email validation
- [ ] Test password mismatch
- [ ] Check JWT tokens are returned on login
- [ ] Check tokens are stored in localStorage
- [ ] Check redirect to dashboard after login
- [ ] Check logout functionality

---

## 🐛 Error Messages Reference

| Error | Cause | Solution |
|-------|-------|----------|
| "Email already registered" | Email exists in database | Use different email |
| "Passwords do not match" | Password ≠ Confirm Password | Match passwords |
| "Password must be at least 8 characters" | Password too short | Use longer password |
| "Password must be 72 characters or less" | Password too long | Use shorter password |
| "Incorrect email or password" | Login credentials wrong | Check credentials |
| "User account is inactive" | User is_active = False | Contact admin |
| "Network Error" | Backend not running | Start backend server |

---

## 📝 Test Data Examples

**Test User 1:**
```
Name: Alice Johnson
Email: alice@test.com
Password: alice12345
Phone: +1234567890
```

**Test User 2:**
```
Name: Bob Smith
Email: bob@test.com
Password: bobpass123
Phone: +9876543210
```

**Test User 3:**
```
Name: Charlie Brown
Email: charlie@test.com
Password: charlie2024
Phone: (optional)
```

---

## 🎉 Success Criteria

Registration is working correctly if:
- ✅ User can fill and submit the form
- ✅ No errors in browser console
- ✅ No errors in backend terminal
- ✅ User is redirected to login page
- ✅ User appears in database
- ✅ User can login with credentials
- ✅ JWT tokens are returned
- ✅ User is redirected to dashboard

---

**🎊 The password error is fixed! Try registering again! 🎊**

If you still encounter issues, check:
1. Backend terminal for errors
2. Browser console for errors
3. Network tab in DevTools
4. Make sure both servers are running

---

*Last Updated: Password bcrypt error fixed*
*Status: Registration working correctly*
