# Risk Profiling Engine - Complete Documentation

## Overview
The Risk Profiling Engine automatically calculates a user's investment risk profile based on their financial profile data. It provides a comprehensive risk score (0-100) and classifies users into investor types to guide portfolio allocation decisions.

## Architecture

### Backend Components

#### 1. Database Model (`backend/app/models/risk_profile.py`)
```python
class RiskProfile:
    - id: Primary key
    - user_id: Foreign key to users table (unique)
    - risk_score: Float (0-100)
    - investor_type: String (Conservative/Moderate/Aggressive)
    - explanation: Text (detailed explanation)
    - created_at: Timestamp
    - updated_at: Timestamp
```

**Relationships:**
- One-to-one with User model
- Automatically created/updated when financial profile changes

#### 2. Risk Calculator Service (`backend/app/services/risk_calculator.py`)

**Core Calculation Logic:**

The risk score is calculated using a weighted average of 5 factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Age | 15% | Younger age = higher risk capacity |
| Income | 10% | Higher income = higher risk capacity |
| Savings Rate | 15% | Higher savings = higher risk capacity |
| Investment Horizon | 25% | Longer horizon = higher risk capacity |
| Risk Tolerance | 35% | User's stated preference (most important) |

**Score Calculation Details:**

1. **Age Score (0-100)**
   - 18-30 years: 90-100 (High risk capacity)
   - 31-40 years: 70-89 (Moderate-high)
   - 41-50 years: 50-69 (Moderate)
   - 51-60 years: 30-49 (Moderate-low)
   - 61+ years: 0-29 (Low risk capacity)

2. **Income Score (0-100)**
   - <₹25K/month: 20-30
   - ₹25K-50K: 40-50
   - ₹50K-75K: 55-65
   - ₹75K-100K: 70-80
   - >₹100K: 85-100

3. **Savings Score (0-100)** - Based on savings rate (savings/income)
   - <10% savings rate: 10-20
   - 10-20%: 30-40
   - 20-30%: 50-60
   - 30-40%: 70-80
   - >40%: 85-100

4. **Investment Horizon Score**
   - 1-3 Years: 20
   - 3-5 Years: 45
   - 5-10 Years: 70
   - 10+ Years: 95

5. **Risk Tolerance Score**
   - Low: 15
   - Medium: 50
   - High: 90

**Investor Type Classification:**
- **Conservative**: 0-39 (Equity 30%, Debt 60%, Gold 10%)
- **Moderate**: 40-69 (Equity 50%, Debt 40%, Gold 10%)
- **Aggressive**: 70-100 (Equity 70%, Debt 20%, Gold 10%)

#### 3. API Endpoints (`backend/app/api/risk.py`)

**POST /api/risk/calculate**
- Calculates/recalculates risk profile
- Requires authentication
- Requires existing financial profile
- Returns: RiskProfileResponse

**GET /api/risk/**
- Retrieves existing risk profile
- Requires authentication
- Returns: RiskProfileResponse
- Returns 404 if not calculated yet

**DELETE /api/risk/**
- Deletes risk profile
- Requires authentication
- Returns: 204 No Content

### Frontend Components

#### 1. Risk Service (`frontend/src/services/riskService.js`)
API client for risk profile operations:
- `calculateRiskProfile()`: Trigger calculation
- `getRiskProfile()`: Fetch existing profile
- `deleteRiskProfile()`: Remove profile

#### 2. Risk Gauge Component (`frontend/src/components/common/RiskGauge.js`)

**Visual gauge visualization featuring:**
- Semi-circular gauge with needle indicator
- Color-coded by investor type:
  - Green: Conservative (0-39)
  - Orange: Moderate (40-69)
  - Red: Aggressive (70-100)
- Displays score, investor type, and legend
- Configurable size prop

#### 3. Risk Assessment Page (`frontend/src/pages/RiskAssessment.js`)

**Features:**
- Check for financial profile prerequisite
- Calculate risk profile button
- Display risk gauge visualization
- Show detailed explanation
- Investment allocation recommendations
- Next steps guidance (Portfolio, SIP, Profile)

**User Flow:**
1. If no financial profile → Redirect to create one
2. If financial profile exists but no risk profile → Show calculate button
3. If risk profile exists → Display full results with gauge
4. Recalculate button available to update

#### 4. Dashboard Integration (`frontend/src/pages/Dashboard.js`)

**Risk Profile Card:**
- Shows risk score in circular display
- Shows investor type badge
- Shows recommended allocations
- Link to detailed analysis
- Status indicator in Quick Actions

## Automatic Risk Calculation

### Trigger Points
Risk profile is automatically calculated:

1. **After Financial Profile Creation**
   - When user creates financial profile for first time
   - Automatically redirects to Risk Assessment page

2. **After Financial Profile Update**
   - When user updates their financial profile
   - Risk profile recalculates with new data
   - Redirects to Risk Assessment to show updated results

3. **Manual Trigger**
   - User can click "Calculate Risk Profile" button
   - User can click "Recalculate Risk Profile" button

### Implementation in FinancialProfile.js
```javascript
// After saving financial profile
await profileService.createProfile(profileData);

// Automatically calculate risk profile
await riskService.calculateRiskProfile();

// Redirect to show results
navigate('/risk-assessment');
```

## Navigation Integration

Risk Assessment is accessible from:
1. **Navbar**: Direct "Risk" link
2. **Dashboard**: Quick Actions card
3. **Dashboard**: Risk Profile card
4. **Financial Profile**: Auto-redirect after save
5. **Direct URL**: `/risk-assessment`

## Data Flow

```
User → Financial Profile Form
  ↓
Save Financial Profile
  ↓
Automatic Risk Calculation
  ↓
Calculate Risk Score (weighted algorithm)
  ↓
Classify Investor Type
  ↓
Generate Explanation
  ↓
Save to Database
  ↓
Display on Risk Assessment Page
  ↓
Show on Dashboard Summary
```

## API Integration

### Request Examples

**Calculate Risk Profile:**
```bash
POST http://localhost:8000/api/risk/calculate
Authorization: Bearer {token}
```

**Get Risk Profile:**
```bash
GET http://localhost:8000/api/risk/
Authorization: Bearer {token}
```

### Response Schema
```json
{
  "id": 1,
  "user_id": 1,
  "risk_score": 65.5,
  "investor_type": "Moderate",
  "explanation": "Your risk profile has been calculated as Moderate...",
  "created_at": "2026-07-12T10:30:00Z",
  "updated_at": "2026-07-12T10:30:00Z"
}
```

## Security

- All endpoints require JWT authentication
- Risk profile is unique per user (one-to-one relationship)
- Users can only access their own risk profile
- Financial profile required before risk calculation

## Error Handling

### Common Errors

1. **404 - Financial Profile Not Found**
   - User hasn't created financial profile yet
   - Frontend shows "Create Financial Profile" prompt

2. **404 - Risk Profile Not Found**
   - Risk profile hasn't been calculated yet
   - Frontend shows "Calculate Risk Profile" button

3. **401 - Unauthorized**
   - Invalid or expired JWT token
   - User needs to login again

## Testing Scenarios

### Manual Testing Flow

1. **New User Flow:**
   - Register new account
   - Login
   - Create financial profile
   - Verify automatic risk calculation
   - Check dashboard shows risk profile

2. **Update Flow:**
   - Update financial profile (change risk tolerance)
   - Verify risk profile recalculates
   - Check new investor type if applicable
   - Verify dashboard updates

3. **Edge Cases:**
   - Try accessing risk assessment without financial profile
   - Try calculating risk without financial profile
   - Update only financial profile without recalculating risk
   - Delete and recreate risk profile

### Test User Profiles

**Conservative Profile:**
- Age: 55
- Income: ₹30,000
- Savings: ₹5,000
- Horizon: 1-3 Years
- Tolerance: Low
- Expected: Conservative (score ~25-35)

**Moderate Profile:**
- Age: 35
- Income: ₹60,000
- Savings: ₹15,000
- Horizon: 5-10 Years
- Tolerance: Medium
- Expected: Moderate (score ~50-60)

**Aggressive Profile:**
- Age: 25
- Income: ₹100,000
- Savings: ₹40,000
- Horizon: 10+ Years
- Tolerance: High
- Expected: Aggressive (score ~75-85)

## Deployment Checklist

### Backend
- [x] Risk Profile model created
- [x] Risk Calculator service implemented
- [x] API routes registered in main.py
- [x] User model has risk_profile relationship
- [x] Database migrations applied

### Frontend
- [x] Risk Service created
- [x] Risk Gauge component created
- [x] Risk Assessment page created
- [x] Dashboard integration complete
- [x] Navbar link added
- [x] Automatic calculation in profile flow

### Integration
- [x] API endpoints working
- [x] Authentication flow working
- [x] Automatic calculation after profile save
- [x] Dashboard displays risk data
- [x] Navigation between pages working

## Future Enhancements

### Potential Improvements
1. **Historical Tracking**: Store risk profile history to show changes over time
2. **Advanced Algorithms**: Machine learning-based risk assessment
3. **Questionnaire**: Additional risk assessment questions beyond financial data
4. **Comparison**: Compare user's risk profile with similar users
5. **Recommendations**: AI-powered investment recommendations based on risk
6. **Alerts**: Notify users when risk profile significantly changes
7. **Portfolio Rebalancing**: Suggest rebalancing when risk profile changes
8. **Risk Scenarios**: Show what-if scenarios for different risk parameters

## Troubleshooting

### Risk Profile Not Calculating
- Verify financial profile exists
- Check backend logs for errors
- Verify JWT token is valid
- Check API endpoint is accessible

### Risk Score Seems Wrong
- Verify input data in financial profile
- Check calculation weights in RiskCalculator
- Review scoring ranges for each factor
- Verify investor type thresholds (40 and 70)

### Dashboard Not Showing Risk Profile
- Check if risk profile was calculated
- Verify API call is successful
- Check browser console for errors
- Verify dashboard fetchData() includes risk profile

## Conclusion

The Risk Profiling Engine is fully implemented and integrated into the application. It provides automatic, intelligent risk assessment based on comprehensive financial data, with a user-friendly visualization and seamless integration throughout the application.

**Key Features:**
✅ Automatic calculation after profile creation/update
✅ Comprehensive scoring algorithm with 5 factors
✅ Visual gauge display
✅ Detailed explanations
✅ Investment allocation recommendations
✅ Dashboard integration
✅ Complete navigation flow

**Status:** ✅ COMPLETE AND READY FOR USE
