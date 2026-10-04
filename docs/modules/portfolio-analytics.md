# Portfolio Risk Analysis Module

## Overview
Comprehensive portfolio risk analysis module with volatility, Sharpe ratio, maximum drawdown calculations, and risk scoring system.

## Status
✅ **COMPLETED**

## Features Implemented

### 1. Backend Components

#### Service Layer (`portfolio_risk_analyzer.py`)
- **Volatility Calculation**: Annualized standard deviation of returns
  - Formula: σ = std(returns) × √252
  - Measures price fluctuation intensity

- **Sharpe Ratio**: Risk-adjusted return metric
  - Formula: (Average Return - Risk Free Rate) / Volatility
  - Interpretation:
    - > 3.0: Excellent
    - > 2.0: Very good
    - > 1.0: Good
    - < 0: Poor

- **Maximum Drawdown**: Largest peak-to-trough decline
  - Formula: (Trough Value - Peak Value) / Peak Value
  - Shows worst-case loss scenario

- **Risk Score**: 0-100 scale weighted metric
  - Volatility: 40%
  - Sharpe Ratio: 30%
  - Max Drawdown: 30%

- **Risk Level Classification**:
  - 0-29: Low
  - 30-49: Moderate
  - 50-69: High
  - 70-100: Very High

- **Sample Data Generator**: For testing purposes
  - Uses geometric Brownian motion
  - Configurable parameters (value, days, volatility, drift)

#### Database Model (`portfolio_analysis.py`)
- Table: `portfolio_analyses`
- Fields:
  - Risk metrics (volatility, sharpe_ratio, max_drawdown)
  - Performance metrics (average_return, total_return)
  - Analysis metadata (data_points, analysis_period_days)
  - Historical data storage (JSON)
  - Timestamps (created_at, updated_at)

#### API Schemas (`portfolio_analysis.py`)
- `PortfolioDataPoint`: Input data point model
- `PortfolioAnalysisRequest`: Request model with validation
- `PortfolioAnalysisResponse`: Complete analysis response
- `RiskInterpretation`: Risk level interpretation and recommendations
- `PortfolioAnalysisDB`: Database model response
- `GenerateSampleDataRequest`: Sample data generation parameters

#### API Endpoints (`portfolio_analysis.py`)
- `POST /api/v1/portfolio-analysis/analyze`: Analyze portfolio risk
- `GET /api/v1/portfolio-analysis/latest`: Get latest analysis
- `GET /api/v1/portfolio-analysis/history`: Get analysis history
- `POST /api/v1/portfolio-analysis/generate-sample-data`: Generate test data
- `DELETE /api/v1/portfolio-analysis/{id}`: Delete analysis

### 2. Frontend Components

#### Service Layer (`portfolioAnalysisService.js`)
- `analyzePortfolio()`: Submit portfolio data for analysis
- `getLatestAnalysis()`: Fetch most recent analysis
- `getAnalysisHistory()`: Fetch historical analyses
- `generateSampleData()`: Generate test portfolio data
- `deleteAnalysis()`: Delete an analysis

#### Portfolio Analytics Page (`PortfolioAnalytics.js`)
**Features:**
- Risk score gauge with color-coded visualization
- Comprehensive risk interpretation with characteristics and recommendations
- Four main metric cards:
  - Volatility (with interpretation)
  - Sharpe Ratio (with interpretation)
  - Maximum Drawdown (with color coding)
  - Total Return (with average annual return)
- Performance metrics panel:
  - Average annual return
  - Risk-free rate
  - Excess return
  - Return per unit risk
- Analysis details panel:
  - Data points count
  - Analysis period
  - Trading days
  - Annualization factor
- Sample data generator with configurable parameters:
  - Initial value
  - Days (30-1260)
  - Volatility (0-1)
  - Expected return (drift)
- Action buttons (Generate, Refresh)

#### Dashboard Integration
- Added "Risk Analysis" quick action card
- Shows risk score badge when analysis exists
- Added "Portfolio Risk Analysis" panel with:
  - Risk score gauge
  - Key metrics (volatility, Sharpe, drawdown, return)
  - Link to detailed analysis page

#### Navigation
- Added "Analytics" link to navbar
- Route: `/portfolio-analytics`
- Accessible from Dashboard and navbar

### 3. Integration

#### Database
- Model registered in `models/__init__.py`
- Relationship added to User model
- Auto-creates table on application startup

#### API Routes
- Registered in `main.py`
- Prefix: `/api/v1/portfolio-analysis`
- Tag: "Portfolio Analysis"
- Protected with JWT authentication

#### Frontend Routing
- Route added to `App.js`
- Component imported: `PortfolioAnalytics`
- Path: `/portfolio-analytics`

## Risk Calculation Details

### Volatility
- **Purpose**: Measures portfolio price fluctuation
- **Calculation**: Standard deviation of daily returns × √252
- **Interpretation**:
  - < 10%: Low volatility (stable)
  - 10-20%: Moderate volatility
  - 20-30%: High volatility
  - > 30%: Very high volatility

### Sharpe Ratio
- **Purpose**: Risk-adjusted performance measure
- **Formula**: (Portfolio Return - Risk-Free Rate) / Portfolio Volatility
- **Interpretation**:
  - > 3: Excellent risk-adjusted returns
  - 2-3: Very good
  - 1-2: Good
  - 0-1: Fair
  - < 0: Poor (underperforming risk-free rate)

### Maximum Drawdown
- **Purpose**: Largest peak-to-trough decline
- **Calculation**: Minimum of (Value - Running Maximum) / Running Maximum
- **Interpretation**:
  - > -10%: Low drawdown (resilient)
  - -10% to -20%: Moderate drawdown
  - -20% to -30%: High drawdown
  - < -30%: Severe drawdown (high risk)

### Risk Score
- **Purpose**: Overall risk assessment (0-100 scale)
- **Weighting**:
  - Volatility: 40% weight
  - Sharpe Ratio: 30% weight (inverted - higher is better)
  - Max Drawdown: 30% weight
- **Classification**:
  - 0-29: Low Risk
  - 30-49: Moderate Risk
  - 50-69: High Risk
  - 70-100: Very High Risk

## Sample Data Generation

The system includes a sample data generator using **Geometric Brownian Motion** (GBM):

**Formula**: dS = μS dt + σS dW
- μ (drift): Expected return rate
- σ (volatility): Standard deviation of returns
- dW: Wiener process (random walk)

**Parameters**:
- Initial Value: Starting portfolio value (default: ₹100,000)
- Days: Simulation period (30-1260 days, default: 252)
- Volatility: Annual volatility (0-1, default: 0.15 or 15%)
- Drift: Expected annual return (default: 0.10 or 10%)

## API Examples

### Analyze Portfolio
```bash
POST /api/v1/portfolio-analysis/analyze
Authorization: Bearer <token>

{
  "portfolio_data": [
    {"date": "2024-01-01", "value": 100000},
    {"date": "2024-01-02", "value": 101000},
    ...
  ],
  "risk_free_rate": 0.06
}
```

### Get Latest Analysis
```bash
GET /api/v1/portfolio-analysis/latest
Authorization: Bearer <token>
```

### Generate Sample Data
```bash
POST /api/v1/portfolio-analysis/generate-sample-data
Authorization: Bearer <token>

{
  "initial_value": 100000,
  "days": 252,
  "volatility": 0.15,
  "drift": 0.10
}
```

## Risk Interpretation & Recommendations

### Low Risk (Score: 0-29)
**Characteristics:**
- Low volatility and stable price movements
- Good risk-adjusted returns (Sharpe ratio)
- Minimal drawdowns during market downturns

**Recommendations:**
- Consider increasing equity allocation for higher growth
- Conservative approach provides stability
- Suitable for near-term goals or risk-averse investors

### Moderate Risk (Score: 30-49)
**Characteristics:**
- Moderate volatility with reasonable fluctuations
- Balanced risk-adjusted returns
- Manageable drawdowns within acceptable range

**Recommendations:**
- Well-balanced portfolio suitable for most investors
- Continue monitoring and rebalancing periodically
- Good for medium to long-term investment goals

### High Risk (Score: 50-69)
**Characteristics:**
- High volatility with substantial price swings
- Risk-return balance may need attention
- Notable drawdowns during market stress

**Recommendations:**
- Consider diversifying to reduce concentration risk
- Review asset allocation and rebalance if needed
- Ensure alignment with your risk tolerance
- Monitor portfolio more frequently

### Very High Risk (Score: 70-100)
**Characteristics:**
- Very high volatility and unpredictable movements
- Poor risk-adjusted returns
- Severe drawdowns that may impact financial goals

**Recommendations:**
- Immediate rebalancing recommended
- Significantly reduce concentration in high-risk assets
- Increase allocation to stable assets
- Consult with a financial advisor
- Not suitable for conservative investors or near-term goals

## Files Created/Modified

### Backend
- ✅ `backend/app/services/portfolio_risk_analyzer.py` (already existed)
- ✅ `backend/app/models/portfolio_analysis.py` (created)
- ✅ `backend/app/schemas/portfolio_analysis.py` (created)
- ✅ `backend/app/api/portfolio_analysis.py` (created)
- ✅ `backend/app/models/__init__.py` (modified)
- ✅ `backend/app/models/user.py` (modified - added relationship)
- ✅ `backend/app/main.py` (modified - registered routes)

### Frontend
- ✅ `frontend/src/services/portfolioAnalysisService.js` (created)
- ✅ `frontend/src/pages/PortfolioAnalytics.js` (created)
- ✅ `frontend/src/pages/Dashboard.js` (modified - added risk analysis panel)
- ✅ `frontend/src/components/Layout/Navbar.js` (modified - added link)
- ✅ `frontend/src/App.js` (modified - added route)

### Documentation
- ✅ `PORTFOLIO_RISK_ANALYSIS.md` (this file)

## Testing Instructions

### 1. Start Backend
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 2. Start Frontend
```bash
cd frontend
npm start
```

### 3. Test Flow
1. Login to the application
2. Navigate to "Analytics" in navbar OR click "Risk Analysis" card on Dashboard
3. Click "Generate & Analyze Sample Data" button
4. Adjust parameters if desired (initial value, days, volatility, drift)
5. View comprehensive risk analysis:
   - Risk score gauge
   - Risk level classification
   - Interpretation and recommendations
   - Volatility, Sharpe ratio, max drawdown metrics
   - Performance metrics
   - Analysis details
6. Navigate to Dashboard to see risk analysis summary
7. Generate multiple analyses to test history tracking

## Dependencies

### Backend
- NumPy (for mathematical calculations)
- FastAPI (API framework)
- SQLAlchemy (database ORM)
- Pydantic (data validation)

### Frontend
- React (UI framework)
- Recharts (for future chart implementations)
- Axios (HTTP client)

## Next Steps (Optional Enhancements)

1. **Historical Charts**: Add line charts showing portfolio value over time
2. **Comparison**: Compare multiple analyses side-by-side
3. **Real Portfolio Integration**: Connect with actual portfolio data
4. **Alerts**: Risk threshold alerts and notifications
5. **Export**: PDF/CSV export of analysis reports
6. **Benchmarking**: Compare against market indices
7. **Monte Carlo**: Probabilistic scenario analysis
8. **Value at Risk (VaR)**: Additional risk metric
9. **Correlation Matrix**: For multi-asset portfolios
10. **Stress Testing**: Simulate market crash scenarios

## Technical Notes

- Risk-free rate default: 6% (typical T-Bill rate)
- Annualization factor: √252 (trading days per year)
- All percentages stored as decimals in database
- Frontend displays percentages with 2 decimal places
- Color coding based on risk levels for better UX
- JWT authentication required for all endpoints
- Database automatically creates tables on startup

## Conclusion

The Portfolio Risk Analysis module is fully implemented and integrated into the application. Users can now:
- Generate sample portfolio data for testing
- Analyze portfolio risk with comprehensive metrics
- View risk scores and classifications
- Get personalized recommendations based on risk level
- Access analysis from both Dashboard and dedicated Analytics page
- Track analysis history

All components are complete, tested, and ready for use. The module provides professional-grade portfolio risk analysis suitable for financial planning applications.
