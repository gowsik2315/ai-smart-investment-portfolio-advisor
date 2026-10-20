"""
Risk Calculation Engine
Automatically calculates risk score from financial profile
"""

from app.models.financial_profile import FinancialProfile


class RiskCalculator:
    """
    Risk profiling engine that calculates risk score based on:
    - Age
    - Income
    - Savings
    - Investment Horizon
    - Risk Tolerance
    
    Score Range: 0-100
    - 0-39: Conservative
    - 40-69: Moderate
    - 70-100: Aggressive
    """
    
    @staticmethod
    def calculate_risk_score(profile: FinancialProfile) -> dict:
        """
        Calculate comprehensive risk score from financial profile
        
        Args:
            profile: FinancialProfile object
            
        Returns:
            dict with risk_score, investor_type, and explanation
        """
        # Initialize score components
        age_score = RiskCalculator._calculate_age_score(profile.age)
        income_score = RiskCalculator._calculate_income_score(profile.monthly_income)
        savings_score = RiskCalculator._calculate_savings_score(
            profile.monthly_income, 
            profile.monthly_savings
        )
        horizon_score = RiskCalculator._calculate_horizon_score(profile.investment_horizon)
        tolerance_score = RiskCalculator._calculate_tolerance_score(profile.risk_tolerance)
        
        # Weighted average calculation
        # Weights: Age(15%), Income(10%), Savings(15%), Horizon(25%), Tolerance(35%)
        weights = {
            'age': 0.15,
            'income': 0.10,
            'savings': 0.15,
            'horizon': 0.25,
            'tolerance': 0.35
        }
        
        total_score = (
            age_score * weights['age'] +
            income_score * weights['income'] +
            savings_score * weights['savings'] +
            horizon_score * weights['horizon'] +
            tolerance_score * weights['tolerance']
        )
        
        # Round to 2 decimal places
        risk_score = round(total_score, 2)
        
        # Determine investor type
        if risk_score < 40:
            investor_type = "Conservative"
        elif risk_score < 70:
            investor_type = "Moderate"
        else:
            investor_type = "Aggressive"
        
        # Generate explanation
        explanation = RiskCalculator._generate_explanation(
            risk_score,
            investor_type,
            age_score,
            income_score,
            savings_score,
            horizon_score,
            tolerance_score,
            profile
        )
        
        return {
            'risk_score': risk_score,
            'investor_type': investor_type,
            'explanation': explanation
        }
    
    @staticmethod
    def _calculate_age_score(age: int) -> float:
        """
        Calculate risk score based on age
        Younger investors can take more risk
        
        Score Distribution:
        - 18-30: 90-100 (High risk capacity)
        - 31-40: 70-89 (Moderate-high)
        - 41-50: 50-69 (Moderate)
        - 51-60: 30-49 (Moderate-low)
        - 61+: 0-29 (Low risk capacity)
        """
        if age <= 30:
            return 90 + ((30 - age) / 12 * 10)  # 90-100
        elif age <= 40:
            return 70 + ((40 - age) / 10 * 20)  # 70-90
        elif age <= 50:
            return 50 + ((50 - age) / 10 * 20)  # 50-70
        elif age <= 60:
            return 30 + ((60 - age) / 10 * 20)  # 30-50
        else:
            return max(0, 30 - ((age - 60) * 3))  # 0-30
    
    @staticmethod
    def _calculate_income_score(monthly_income: float) -> float:
        """
        Calculate risk score based on income
        Higher income = higher risk capacity
        
        Score Distribution:
        - <25K: 20-30
        - 25K-50K: 40-50
        - 50K-75K: 55-65
        - 75K-100K: 70-80
        - >100K: 85-100
        """
        if monthly_income < 25000:
            return 20 + (monthly_income / 25000 * 10)
        elif monthly_income < 50000:
            return 40 + ((monthly_income - 25000) / 25000 * 10)
        elif monthly_income < 75000:
            return 55 + ((monthly_income - 50000) / 25000 * 10)
        elif monthly_income < 100000:
            return 70 + ((monthly_income - 75000) / 25000 * 10)
        else:
            return min(100, 85 + ((monthly_income - 100000) / 100000 * 15))
    
    @staticmethod
    def _calculate_savings_score(monthly_income: float, monthly_savings: float) -> float:
        """
        Calculate risk score based on savings rate
        Higher savings rate = higher risk capacity
        
        Score Distribution:
        - <10% savings rate: 10-20
        - 10-20%: 30-40
        - 20-30%: 50-60
        - 30-40%: 70-80
        - >40%: 85-100
        """
        if monthly_income == 0:
            return 0
        
        savings_rate = (monthly_savings / monthly_income) * 100
        
        if savings_rate < 10:
            return 10 + (savings_rate * 1)
        elif savings_rate < 20:
            return 30 + ((savings_rate - 10) * 1)
        elif savings_rate < 30:
            return 50 + ((savings_rate - 20) * 1)
        elif savings_rate < 40:
            return 70 + ((savings_rate - 30) * 1)
        else:
            return min(100, 85 + ((savings_rate - 40) * 0.75))
    
    @staticmethod
    def _calculate_horizon_score(investment_horizon: str) -> float:
        """
        Calculate risk score based on investment horizon
        Longer horizon = higher risk capacity
        
        Score Distribution:
        - 1-3 Years: 20
        - 3-5 Years: 45
        - 5-10 Years: 70
        - 10+ Years: 95
        """
        horizon_mapping = {
            "1-3 Years": 20,
            "3-5 Years": 45,
            "5-10 Years": 70,
            "10+ Years": 95
        }
        return horizon_mapping.get(investment_horizon, 50)
    
    @staticmethod
    def _calculate_tolerance_score(risk_tolerance: str) -> float:
        """
        Calculate risk score based on stated risk tolerance
        This is the most important factor (35% weight)
        
        Score Distribution:
        - Low: 15
        - Medium: 50
        - High: 90
        """
        tolerance_mapping = {
            "Low": 15,
            "Medium": 50,
            "High": 90
        }
        return tolerance_mapping.get(risk_tolerance, 50)
    
    @staticmethod
    def _generate_explanation(
        risk_score: float,
        investor_type: str,
        age_score: float,
        income_score: float,
        savings_score: float,
        horizon_score: float,
        tolerance_score: float,
        profile: FinancialProfile
    ) -> str:
        """Generate detailed explanation of risk calculation"""
        
        savings_rate = (profile.monthly_savings / profile.monthly_income * 100) if profile.monthly_income > 0 else 0
        allocation = RiskCalculator._allocation_for(risk_score)

        explanation = f"""Your risk profile has been calculated as {investor_type} with a score of {risk_score}/100.

Factors considered:
• Age ({profile.age} years): Score {age_score:.1f}/100 - {'Younger age allows for higher risk capacity' if age_score > 70 else 'Age suggests moderate to conservative approach' if age_score > 40 else 'Age suggests conservative approach'}
• Income (₹{profile.monthly_income:,.0f}/month): Score {income_score:.1f}/100 - {'Strong income supports risk capacity' if income_score > 70 else 'Moderate income suggests balanced approach' if income_score > 40 else 'Income level suggests conservative approach'}
• Savings Rate ({savings_rate:.1f}%): Score {savings_score:.1f}/100 - {'Excellent savings rate supports risk-taking' if savings_rate > 30 else 'Good savings habit' if savings_rate > 20 else 'Building savings is important'}
• Investment Horizon ({profile.investment_horizon}): Score {horizon_score:.1f}/100 - {'Long-term horizon allows for aggressive strategy' if horizon_score > 70 else 'Medium-term allows moderate risk' if horizon_score > 40 else 'Short-term requires conservative approach'}
• Risk Tolerance ({profile.risk_tolerance}): Score {tolerance_score:.1f}/100 - Your stated preference is the key factor

Recommended Investment Allocation:
• Stocks: {allocation['stocks_percent']}%
• Mutual Funds: {allocation['mutual_funds_percent']}%
• Gold: {allocation['gold_percent']}%
• Emergency Fund: {allocation['emergency_percent']}%

This profile will help guide your investment decisions and portfolio allocation."""
        
        return explanation
    
    @staticmethod
    def _allocation_for(risk_score: float) -> dict:
        """
        The allocation this score implies.

        Delegates to RecommendationEngine so the Risk page and the
        Recommendation page cannot disagree. They previously did: this
        module carried its own three-tier table (Aggressive = 70/20/10)
        while the engine computed a score-proportional split, so one
        user saw two different "recommended" allocations.
        """
        from app.services.recommendation_engine import RecommendationEngine

        return RecommendationEngine._calculate_dynamic_allocation(risk_score)
