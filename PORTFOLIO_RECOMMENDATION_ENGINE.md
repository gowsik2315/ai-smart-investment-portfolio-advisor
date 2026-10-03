# Portfolio Recommendation Engine - Complete Documentation

## Overview
The Portfolio Recommendation Engine automatically generates personalized asset allocation strategies based on the user's risk profile. It provides specific percentage allocations across four key asset classes: Stocks, Mutual Funds, Gold, and Emergency Fund.

---

## Architecture

### Backend Components

#### 1. Database Model (`backend/app/models/portfolio_recommendation.py`)

```python
class PortfolioRecommendation:
    - id: Primary key
    - user_id: Foreign key to users table (unique)
    - stocks_percent: Float (percentage allocation)
    - mutual_funds_percent: Float (percentage allocation)
    - gold_percent: Float (percentage allocation)
    - emergency_percent: Float (percentage allocation)
    - recommendation_summary: Text (detailed explanation)
    - created_at: Timestamp
    - updated_at: Timestamp
```

**Relationships:**
- One-to-one with User model
- Automatically generated after risk profile calculation

#### 2. Recommendation Engine Service (`backend/app/services/recommendation_engine.py`)

**Allocation Strategies:**

| Investor Type | Stocks | Mutual Funds | Gold | Emergency Fund |
|---------------|--------|--------------|------|----------------|
| Conservative  | 20%    | 50%          | 20%  | 10%            |
| Moderate      | 45%    | 35%          | 10%  | 10%            |
| Aggressive    | 70%    | 20%          | 5%   | 5%             |

**Key Features:**
- Pre-defined allocation strategies by risk type
- Detailed summary generation with investment guidance
- Product recommendations for each asset class
- Monthly investment examples
- Investor-specific advice

**Summary Includes:**
- Allocation breakdown
- Strategy explanation
- Recommended products
- Investment examples
- Key principles
- Next steps
- Disclaimer

#### 3. Pydantic Schemas (`backend/app/schemas/portfolio_recommendation.py`)

```python
class PortfolioRecommendationBase:
    - stocks_percent: float (0-100)
    - mutual_funds_percent: float (0-100)
    - gold_percent: float (0-100)
    - emergency_percent: float (0-100)
    - recommendation_summary: Optional[str]
```

**Validation:**
- All percentages must be between 0 and 100
- Automatic validation using Pydantic

#### 4. API Endpoints (`backend/app/api/recommendation.py`)

**POST /api/recommendation/generate**
- Generates portfolio recommendation
- Requires risk profile to exist
- Returns complete recommendation with summary

**GET /api/recommendation/**
- Retrieves existing recommendation
- Returns 404 if not generated yet

**DELETE /api/recommendation/**
- Deletes portfolio recommendation
- Returns 204 No Content

---

### Frontend Components

#### 1. Recommendation Service (`frontend/src/services/recommendationService.js`)

API client for portfolio recommendations:
- `generateRecommendation()`: Create/update recommendation
- `getRecommendation()`: Fetch existing recommendation
- `deleteRecommendation()`: Remove recommendation

#### 2. Pie Chart Component (`frontend/src/components/common/PieChart.js`)

**Features:**
- SVG-based donut chart
- Color-coded asset classes
- Interactive hover effects
- Automatic percentage calculation
- Responsive legend
- Customizable size

**Colors:**
- Stocks: Blue (#3b82f6)
- Mutual Funds: Green (#10b981)
- Gold: Orange (#f59e0b)
- Emergency Fund: Red (#ef4444)

#### 3. Portfolio Recommendation Page (`frontend/src/pages/PortfolioRecommendation.js`)

**Sections:**
1. **Header** - Title and description
2. **Risk Profile Check** - Prerequisite validation
3. **Generate Button** - For first-time users
4. **Pie Chart** - Visual allocation display
5. **Allocation Cards** - Four cards with percentages
6. **Detailed Summary** - Complete recommendation text
7. **Next Steps** - Links to SIP and Portfolio

**User Flow:**
- Check if risk profile exists
- Generate recommendation button (if needed)
- Display pie chart visualization
- Show allocation cards
- Present detailed summary
- Provide next action links

---

## Allocation Strategies Explained

### Conservative Strategy (Risk Score 0-39)

**Portfolio Mix:**
- **Stocks: 20%** - Blue-chip stocks, large-cap equity funds
- **Mutual Funds: 50%** - Debt funds, balanced hybrid funds
- **Gold: 20%** - Sovereign Gold Bonds, Gold ETFs
- **Emergency Fund: 10%** - Liquid funds, FDs

**Target Audience:**
- Near retirement
- Low risk tolerance
- Capital preservation priority
- Stable income needs

**Recommended Products:**
- Debt Mutual Funds (Corporate bond funds, Banking & PSU funds)
- Large-cap Equity Funds
- Dividend yield funds
- Sovereign Gold Bonds
- Liquid funds

---

### Moderate Strategy (Risk Score 40-69)

**Portfolio Mix:**
- **Stocks: 45%** - Mix of large-cap and mid-cap stocks
- **Mutual Funds: 35%** - Hybrid funds, balanced advantage funds
- **Gold: 10%** - Gold ETFs, Digital Gold
- **Emergency Fund: 10%** - Liquid funds, ultra-short duration funds

**Target Audience:**
- Mid-career professionals
- Balanced approach
- 5-10 year investment horizon
- Growth with stability

**Recommended Products:**
- Flexi-cap funds
- Multi-cap funds
- Index funds
- Balanced advantage funds
- Aggressive hybrid funds
- Gold ETFs

---

### Aggressive Strategy (Risk Score 70-100)

**Portfolio Mix:**
- **Stocks: 70%** - Growth stocks across all market caps
- **Mutual Funds: 20%** - Small-cap, mid-cap, sectoral funds
- **Gold: 5%** - Minimal allocation for insurance
- **Emergency Fund: 5%** - Essential liquidity only

**Target Audience:**
- Young investors
- High risk tolerance
- Long-term horizon (10+ years)
- Maximum growth focus

**Recommended Products:**
- Small-cap funds
- Mid-cap funds
- Sectoral funds
- Growth stocks
- Thematic funds
- Gold ETFs

---

## Integration Points

### Automatic Generation Flow

```
User Creates Financial Profile
         ↓
Risk Profile Calculated
         ↓
Portfolio Recommendation Generated (Automatic)
         ↓
User Views Pie Chart & Details
         ↓
User Proceeds to SIP/Portfolio
```

### Trigger Points

1. **After Risk Calculation** ✅
   - Automatically generates recommendation
   - Silent background operation
   - Logs errors without user notification

2. **Manual Generation** ✅
   - User clicks "Generate Recommendation"
   - Regenerate button for updates
   - Immediate feedback

3. **When Risk Changes** ✅
   - Risk profile update triggers new recommendation
   - Allocation adjusts to new investor type
   - Summary updates with new data

---

## Database Schema

```sql
CREATE TABLE portfolio_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    stocks_percent REAL NOT NULL,
    mutual_funds_percent REAL NOT NULL,
    gold_percent REAL NOT NULL,
    emergency_percent REAL NOT NULL,
    recommendation_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## API Documentation

### Generate Recommendation

**Request:**
```bash
POST /api/recommendation/generate
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "stocks_percent": 45.0,
  "mutual_funds_percent": 35.0,
  "gold_percent": 10.0,
  "emergency_percent": 10.0,
  "recommendation_summary": "Portfolio Recommendation for Moderate Investor...",
  "created_at": "2026-07-12T10:30:00Z",
  "updated_at": "2026-07-12T10:30:00Z"
}
```

### Get Recommendation

**Request:**
```bash
GET /api/recommendation/
Authorization: Bearer {token}
```

**Response:** Same as above

### Delete Recommendation

**Request:**
```bash
DELETE /api/recommendation/
Authorization: Bearer {token}
```

**Response:** 204 No Content

---

## UI Components

### Pie Chart Visualization

**Features:**
- Donut-style chart
- Color-coded segments
- Interactive tooltips
- Percentage labels
- Responsive legend
- Clean, modern design

**Implementation:**
- Pure SVG (no external libraries)
- Automatic angle calculation
- Dynamic path generation
- Smooth transitions

### Allocation Cards

**4 Cards Display:**
1. **Stocks Card** (Blue) - Direct equity investments
2. **Mutual Funds Card** (Green) - Diversified fund investments
3. **Gold Card** (Yellow) - Precious metal allocation
4. **Emergency Fund Card** (Red) - Liquid safety net

Each card shows:
- Icon
- Asset class name
- Percentage (large, bold)
- Brief description

---

## User Experience

### Navigation Flow

1. **Dashboard** → "Portfolio Advice" Quick Action
2. **Risk Assessment** → "View Portfolio Recommendation" link
3. **Navbar** → "Recommendations" direct link
4. **Direct URL** → /portfolio-recommendation

### Error Handling

**No Risk Profile:**
- Shows warning card
- "Risk Profile Required" message
- Link to Risk Assessment page

**No Recommendation:**
- Shows generate button
- Clear call-to-action
- Explanation of what will happen

**Generation Error:**
- Red error banner
- Specific error message
- Retry option

---

## Security

- ✅ JWT authentication required
- ✅ User-specific recommendations
- ✅ One-to-one user relationship
- ✅ Risk profile prerequisite enforced
- ✅ Input validation (percentages 0-100)

---

## Testing Scenarios

### Test Case 1: Conservative Profile
**Input:**
- Risk Type: Conservative
- Risk Score: 30

**Expected Output:**
- Stocks: 20%
- Mutual Funds: 50%
- Gold: 20%
- Emergency: 10%
- Summary includes conservative strategy guidance

### Test Case 2: Moderate Profile
**Input:**
- Risk Type: Moderate
- Risk Score: 55

**Expected Output:**
- Stocks: 45%
- Mutual Funds: 35%
- Gold: 10%
- Emergency: 10%
- Summary includes moderate strategy guidance

### Test Case 3: Aggressive Profile
**Input:**
- Risk Type: Aggressive
- Risk Score: 80

**Expected Output:**
- Stocks: 70%
- Mutual Funds: 20%
- Gold: 5%
- Emergency: 5%
- Summary includes aggressive strategy guidance

---

## Monthly Investment Examples

If monthly savings = ₹20,000:

**Conservative:**
- Stocks: ₹4,000
- Mutual Funds: ₹10,000
- Gold: ₹4,000
- Emergency: ₹2,000

**Moderate:**
- Stocks: ₹9,000
- Mutual Funds: ₹7,000
- Gold: ₹2,000
- Emergency: ₹2,000

**Aggressive:**
- Stocks: ₹14,000
- Mutual Funds: ₹4,000
- Gold: ₹1,000
- Emergency: ₹1,000

---

## Key Principles Included

1. **Diversification** - Reduces overall risk
2. **SIP Investing** - Smooths market volatility
3. **Quarterly Review** - Stay on track
4. **Long-term Focus** - Avoid emotional decisions
5. **Emergency Priority** - Build safety net first

---

## Next Steps Guidance

After viewing recommendation:
1. ✅ **Start SIP** - Link to SIP Planner
2. ✅ **Build Portfolio** - Link to Portfolio page
3. ✅ **Review Risk** - Link back to Risk Assessment

---

## Deployment Checklist

### Backend
- [x] Database model created
- [x] Recommendation engine implemented
- [x] Pydantic schemas defined
- [x] API routes created
- [x] Routes registered in main.py
- [x] User relationship configured

### Frontend
- [x] Recommendation service created
- [x] Pie chart component created
- [x] Recommendation page created
- [x] Dashboard integration
- [x] Risk assessment integration
- [x] Navigation updated
- [x] Routes configured

### Integration
- [x] API endpoints working
- [x] Automatic generation after risk calculation
- [x] Pie chart rendering correctly
- [x] Navigation flow complete
- [x] Error handling implemented

---

## Status: ✅ COMPLETE

**All components implemented and integrated.**

### What Works:
✅ Automatic recommendation generation  
✅ Three allocation strategies  
✅ Detailed summary with guidance  
✅ Beautiful pie chart visualization  
✅ Four allocation cards  
✅ Dashboard integration  
✅ Navigation flow  
✅ Error handling  

### Ready For:
✅ Testing with real users  
✅ Integration with actual portfolio  
✅ Integration with SIP planner  
✅ Production deployment  

---

**Last Updated:** July 12, 2026  
**Version:** 1.0  
**Status:** Production Ready ✅
