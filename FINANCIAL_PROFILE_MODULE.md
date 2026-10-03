# Financial Profile Module

## Overview
The Financial Profile Module allows authenticated users to create and manage their financial information, which is used to provide personalized investment recommendations.

## Features

### Backend Features
- ✅ JWT-based authentication for all endpoints
- ✅ CRUD operations for financial profiles
- ✅ Validation of financial data
- ✅ One profile per user constraint
- ✅ SQLite database storage
- ✅ RESTful API design

### Frontend Features
- ✅ Modern, responsive form design
- ✅ Real-time form validation with error messages
- ✅ Financial summary dashboard
- ✅ Auto-load existing profile for updates
- ✅ Success/error notifications
- ✅ Automatic redirect after save

## Database Schema

### FinancialProfile Table
```sql
CREATE TABLE financial_profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    age INTEGER NOT NULL,
    monthly_income FLOAT NOT NULL,
    monthly_savings FLOAT NOT NULL,
    investment_horizon VARCHAR NOT NULL,
    risk_tolerance VARCHAR NOT NULL,
    financial_goal VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## API Endpoints

### 1. Create Financial Profile
**POST** `/api/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "age": 30,
  "monthly_income": 75000,
  "monthly_savings": 25000,
  "investment_horizon": "5-10 Years",
  "risk_tolerance": "Medium",
  "financial_goal": "Wealth Creation"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "age": 30,
  "monthly_income": 75000.0,
  "monthly_savings": 25000.0,
  "investment_horizon": "5-10 Years",
  "risk_tolerance": "Medium",
  "financial_goal": "Wealth Creation",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null
}
```

### 2. Get Financial Profile
**GET** `/api/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "age": 30,
  "monthly_income": 75000.0,
  "monthly_savings": 25000.0,
  "investment_horizon": "5-10 Years",
  "risk_tolerance": "Medium",
  "financial_goal": "Wealth Creation",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null
}
```

### 3. Update Financial Profile
**PUT** `/api/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** (all fields optional)
```json
{
  "monthly_savings": 30000,
  "risk_tolerance": "High"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "age": 30,
  "monthly_income": 75000.0,
  "monthly_savings": 30000.0,
  "investment_horizon": "5-10 Years",
  "risk_tolerance": "High",
  "financial_goal": "Wealth Creation",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T11:45:00"
}
```

### 4. Delete Financial Profile
**DELETE** `/api/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

## Field Options

### Investment Horizon
- `1-3 Years` - Short-term investments
- `3-5 Years` - Medium-term investments
- `5-10 Years` - Long-term investments
- `10+ Years` - Very long-term investments

### Risk Tolerance
- `Low` - Prefer stable, predictable returns
- `Medium` - Can accept moderate fluctuations
- `High` - Can handle significant market volatility

### Financial Goal
- `Wealth Creation` - Growing wealth over time
- `Retirement` - Planning for retirement
- `House Purchase` - Saving for a home
- `Education` - Funding education expenses
- `Emergency Fund` - Building an emergency reserve

## Validation Rules

### Age
- Must be between 18 and 100
- Required field

### Monthly Income
- Must be greater than 0
- Required field
- Numeric format with 2 decimal places

### Monthly Savings
- Must be greater than or equal to 0
- Cannot exceed monthly income
- Required field
- Numeric format with 2 decimal places

### Investment Horizon
- Must be one of the predefined options
- Required field

### Risk Tolerance
- Must be one of: Low, Medium, High
- Required field

### Financial Goal
- Must be one of the predefined options
- Required field

## Frontend Components

### FinancialProfile Page
**Location:** `frontend/src/pages/FinancialProfile.js`

**Features:**
- Modern validated form
- Real-time field validation
- Financial summary dashboard
- Auto-load existing profile
- Success/error notifications
- Responsive design

### Select Component
**Location:** `frontend/src/components/common/Select.js`

**Props:**
- `label` - Field label
- `name` - Field name
- `value` - Current value
- `onChange` - Change handler
- `options` - Array of options
- `required` - Is field required
- `error` - Error message
- `helpText` - Help text below field
- `placeholder` - Placeholder text

## Usage Examples

### Creating a Profile (Frontend)
```javascript
import profileService from '../services/profileService';

const profileData = {
  age: 28,
  monthly_income: 60000,
  monthly_savings: 18000,
  investment_horizon: '5-10 Years',
  risk_tolerance: 'Medium',
  financial_goal: 'Retirement'
};

const profile = await profileService.createProfile(profileData);
```

### Getting a Profile (Frontend)
```javascript
const profile = await profileService.getProfile();
console.log(profile);
```

### Updating a Profile (Frontend)
```javascript
const updates = {
  monthly_savings: 20000,
  risk_tolerance: 'High'
};

const updatedProfile = await profileService.updateProfile(updates);
```

## Testing the Module

### 1. Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Start Frontend Server
```bash
cd frontend
npm start
```

### 3. Test Flow
1. Register a new user at `/register`
2. Login at `/login`
3. Navigate to `/profile`
4. Fill in the financial profile form
5. Submit to create profile
6. Return to `/profile` to see profile loaded
7. Update any fields and submit to update

### 4. API Testing with cURL

**Create Profile:**
```bash
curl -X POST http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer <your_token>" \
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

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer <your_token>"
```

## Error Handling

### Common Error Responses

**401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

**400 Bad Request - Profile Already Exists**
```json
{
  "detail": "Financial profile already exists. Use PUT to update."
}
```

**400 Bad Request - Validation Error**
```json
{
  "detail": "Monthly savings cannot exceed monthly income"
}
```

**404 Not Found**
```json
{
  "detail": "Financial profile not found"
}
```

## Security Notes

- All endpoints require JWT authentication
- User can only access their own profile
- Tokens are stored in localStorage
- Password encryption is currently disabled (development only)
- **DO NOT use in production without enabling password hashing**

## Future Enhancements

- [ ] Add profile completion percentage
- [ ] Add investment recommendations based on profile
- [ ] Add profile history tracking
- [ ] Add more financial fields (debts, assets, etc.)
- [ ] Add profile sharing for advisors
- [ ] Add multi-currency support
- [ ] Add profile export functionality
- [ ] Add profile analytics dashboard

## Dependencies

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- python-jose - JWT handling
- SQLite - Database

### Frontend
- React - UI framework
- React Router - Routing
- Axios - HTTP client
- Tailwind CSS - Styling

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── profile.py          # Profile API routes
│   ├── models/
│   │   └── financial_profile.py # Profile database model
│   ├── schemas/
│   │   └── financial_profile.py # Profile validation schemas
│   └── core/
│       └── security.py          # JWT authentication

frontend/
├── src/
│   ├── pages/
│   │   └── FinancialProfile.js  # Profile form page
│   ├── components/
│   │   └── common/
│   │       └── Select.js        # Select dropdown component
│   ├── services/
│   │   └── profileService.js    # Profile API client
│   └── context/
│       └── AuthContext.js       # Authentication context
```

## Support

For issues or questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review error messages in browser console
3. Check backend logs for detailed errors
4. Verify authentication token is valid
