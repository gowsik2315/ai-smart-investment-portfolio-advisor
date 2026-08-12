"""
Portfolio Recommendation Engine
Generates asset allocation recommendations based on risk profile
"""

from typing import Dict


class RecommendationEngine:
    """
    Portfolio recommendation engine that generates allocation based on investor type
    
    Conservative: Stocks 20%, Mutual Funds 50%, Gold 20%, Emergency 10%
    Moderate: Stocks 45%, Mutual Funds 35%, Gold 10%, Emergency 10%
    Aggressive: Stocks 70%, Mutual Funds 20%, Gold 5%, Emergency 5%
    """
    
    # Allocation mappings by investor type
    ALLOCATION_STRATEGIES = {
        "Conservative": {
            "stocks_percent": 20.0,
            "mutual_funds_percent": 50.0,
            "gold_percent": 20.0,
            "emergency_percent": 10.0
        },
        "Moderate": {
            "stocks_percent": 45.0,
            "mutual_funds_percent": 35.0,
            "gold_percent": 10.0,
            "emergency_percent": 10.0
        },
        "Aggressive": {
            "stocks_percent": 70.0,
            "mutual_funds_percent": 20.0,
            "gold_percent": 5.0,
            "emergency_percent": 5.0
        }
    }
    
    @staticmethod
    def generate_recommendation(investor_type: str, risk_score: float, monthly_savings: float = None) -> Dict:
        """
        Generate portfolio recommendation based on risk score (dynamic allocation)
        
        Args:
            investor_type: Conservative, Moderate, or Aggressive (for display/summary)
            risk_score: Risk score (0-100) - used for calculating allocation
            monthly_savings: Optional monthly savings amount for examples
            
        Returns:
            dict with allocation percentages and summary
        """
        # Calculate dynamic allocation based on risk score
        allocation = RecommendationEngine._calculate_dynamic_allocation(risk_score)
        
        # Generate summary
        summary = RecommendationEngine._generate_summary(
            investor_type,
            risk_score,
            allocation,
            monthly_savings
        )
        
        return {
            "stocks_percent": allocation["stocks_percent"],
            "mutual_funds_percent": allocation["mutual_funds_percent"],
            "gold_percent": allocation["gold_percent"],
            "emergency_percent": allocation["emergency_percent"],
            "recommendation_summary": summary
        }
    
    @staticmethod
    def _calculate_dynamic_allocation(risk_score: float) -> Dict:
        """
        Calculate dynamic allocation based on risk score (0-100)
        
        Formula approach:
        - Stocks: Increases linearly with risk score (10% at 0 → 75% at 100)
        - Mutual Funds: Decreases as risk increases (60% at 0 → 15% at 100)
        - Gold: Decreases slightly (20% at 0 → 5% at 100)
        - Emergency: Decreases with risk tolerance (10% at 0 → 5% at 100)
        
        Args:
            risk_score: Risk score from 0-100
            
        Returns:
            dict with allocation percentages
        """
        # Clamp risk score between 0 and 100
        risk_score = max(0.0, min(100.0, risk_score))
        
        # Calculate stock allocation (10% to 75%)
        # Linear interpolation: 10 + (risk_score / 100) * (75 - 10)
        stocks_percent = 10.0 + (risk_score / 100.0) * 65.0
        
        # Calculate mutual funds allocation (60% to 15%)
        # Inverse linear: 60 - (risk_score / 100) * (60 - 15)
        mutual_funds_percent = 60.0 - (risk_score / 100.0) * 45.0
        
        # Calculate gold allocation (20% to 5%)
        gold_percent = 20.0 - (risk_score / 100.0) * 15.0
        
        # Calculate emergency fund allocation (10% to 5%)
        emergency_percent = 10.0 - (risk_score / 100.0) * 5.0
        
        # Round to 1 decimal place
        stocks_percent = round(stocks_percent, 1)
        mutual_funds_percent = round(mutual_funds_percent, 1)
        gold_percent = round(gold_percent, 1)
        emergency_percent = round(emergency_percent, 1)
        
        # Ensure total is 100% (adjust mutual funds if needed due to rounding)
        total = stocks_percent + mutual_funds_percent + gold_percent + emergency_percent
        if total != 100.0:
            mutual_funds_percent = round(mutual_funds_percent + (100.0 - total), 1)
        
        return {
            "stocks_percent": stocks_percent,
            "mutual_funds_percent": mutual_funds_percent,
            "gold_percent": gold_percent,
            "emergency_percent": emergency_percent
        }
    
    @staticmethod
    def _generate_summary(
        investor_type: str,
        risk_score: float,
        allocation: Dict,
        monthly_savings: float = None
    ) -> str:
        """Generate detailed recommendation summary"""
        
        # Base summary
        summary = f"""Portfolio Recommendation for {investor_type} Investor (Risk Score: {risk_score:.1f})

Your personalized asset allocation strategy:

📊 ALLOCATION BREAKDOWN:
• Stocks: {allocation['stocks_percent']:.0f}%
• Mutual Funds: {allocation['mutual_funds_percent']:.0f}%
• Gold: {allocation['gold_percent']:.0f}%
• Emergency Fund: {allocation['emergency_percent']:.0f}%

"""
        
        # Add investor type specific guidance
        if investor_type == "Conservative":
            summary += """🛡️ CONSERVATIVE STRATEGY:
Your portfolio prioritizes capital preservation with steady growth:

✓ High Mutual Funds Allocation (50%):
  - Focus on debt funds and balanced hybrid funds
  - Provides stable returns with lower volatility
  - Monthly income potential through dividend plans

✓ Moderate Stock Exposure (20%):
  - Blue-chip stocks with strong dividend history
  - Large-cap equity funds
  - Lower risk, steady appreciation

✓ Gold Investment (20%):
  - Hedge against inflation
  - Portfolio diversification
  - Sovereign Gold Bonds or Gold ETFs

✓ Emergency Fund (10%):
  - Liquid funds or high-interest savings
  - 3-6 months of expenses
  - Immediate accessibility

RECOMMENDED PRODUCTS:
• Debt Mutual Funds: Corporate bond funds, Banking & PSU funds
• Equity Funds: Large-cap funds, Dividend yield funds
• Gold: Sovereign Gold Bonds, Gold ETFs
• Emergency: Liquid funds, Fixed deposits
"""
        
        elif investor_type == "Moderate":
            summary += """⚖️ MODERATE STRATEGY:
Your portfolio balances growth potential with risk management:

✓ Balanced Stock Allocation (45%):
  - Mix of large-cap and mid-cap stocks
  - Diversified equity mutual funds
  - Growth with moderate volatility

✓ Mutual Funds (35%):
  - Hybrid funds (equity + debt)
  - Balanced advantage funds
  - Flexible asset allocation

✓ Gold Investment (10%):
  - Portfolio stabilizer
  - Inflation protection
  - Gold ETFs or Digital Gold

✓ Emergency Fund (10%):
  - Liquid funds
  - Ultra-short duration funds
  - Quick access to cash

RECOMMENDED PRODUCTS:
• Equity Funds: Flexi-cap funds, Multi-cap funds, Index funds
• Hybrid Funds: Balanced advantage funds, Aggressive hybrid funds
• Stocks: Mix of large-cap and selected mid-cap stocks
• Gold: Gold ETFs, Digital Gold
• Emergency: Liquid funds, Savings account
"""
        
        else:  # Aggressive
            summary += """🚀 AGGRESSIVE STRATEGY:
Your portfolio maximizes growth potential with higher risk tolerance:

✓ High Stock Allocation (70%):
  - Growth stocks across market caps
  - Sector-specific opportunities
  - Potential for high returns

✓ Mutual Funds (20%):
  - Pure equity funds
  - Small-cap and mid-cap funds
  - Thematic and sectoral funds

✓ Gold Investment (5%):
  - Minimal allocation
  - Basic portfolio insurance
  - Gold ETFs

✓ Emergency Fund (5%):
  - Essential liquidity
  - 3 months expenses minimum
  - Liquid funds

RECOMMENDED PRODUCTS:
• Equity Funds: Small-cap funds, Mid-cap funds, Sectoral funds
• Stocks: Growth stocks, Mid-cap stocks, Small-cap opportunities
• Gold: Gold ETFs, Gold mutual funds
• Emergency: Liquid funds, High-yield savings

⚠️ IMPORTANT: Regular monitoring and rebalancing required
"""
        
        # Add monthly investment example if provided
        if monthly_savings and monthly_savings > 0:
            summary += f"\n💰 MONTHLY INVESTMENT EXAMPLE (₹{monthly_savings:,.0f}):\n"
            summary += f"• Stocks: ₹{monthly_savings * allocation['stocks_percent'] / 100:,.0f}\n"
            summary += f"• Mutual Funds: ₹{monthly_savings * allocation['mutual_funds_percent'] / 100:,.0f}\n"
            summary += f"• Gold: ₹{monthly_savings * allocation['gold_percent'] / 100:,.0f}\n"
            summary += f"• Emergency Fund: ₹{monthly_savings * allocation['emergency_percent'] / 100:,.0f}\n"
        
        # General advice
        summary += """
📌 KEY PRINCIPLES:
1. Diversification reduces risk
2. Regular investments (SIP) smooth out volatility
3. Review and rebalance quarterly
4. Stay invested for long-term goals
5. Avoid emotional decisions during market swings

🎯 NEXT STEPS:
1. Start with emergency fund building
2. Set up SIPs for mutual funds
3. Research and select quality stocks
4. Invest in gold through digital/ETF route
5. Track and review monthly

⚠️ DISCLAIMER: This is an automated recommendation based on your risk profile. 
Consult a SEBI registered financial advisor for personalized advice.
"""
        
        return summary
