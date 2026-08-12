"""
SIP Calculator Service
Implements SIP (Systematic Investment Plan) calculation formulas
"""

from typing import Dict, List
import math


class SIPCalculator:
    """
    SIP calculator that computes future value, total invested, and wealth generated
    
    Formula: FV = P × ({[1 + r]^n - 1} / r) × (1 + r)
    Where:
    - FV = Future Value
    - P = Monthly Investment
    - r = Monthly rate of return (annual rate / 12 / 100)
    - n = Total number of payments (years × 12)
    """
    
    @staticmethod
    def calculate_sip(
        monthly_investment: float,
        annual_return_rate: float,
        investment_duration_years: int
    ) -> Dict:
        """
        Calculate SIP returns
        
        Args:
            monthly_investment: Amount invested monthly (e.g., 5000)
            annual_return_rate: Expected annual return percentage (e.g., 12 for 12%)
            investment_duration_years: Investment period in years (e.g., 10)
            
        Returns:
            dict with total_invested, wealth_generated, future_value, and yearly_breakdown
        """
        # Input validation
        if monthly_investment <= 0:
            raise ValueError("Monthly investment must be greater than 0")
        if annual_return_rate < 0:
            raise ValueError("Annual return rate cannot be negative")
        if investment_duration_years <= 0:
            raise ValueError("Investment duration must be greater than 0")
        
        # Convert annual rate to monthly rate
        monthly_rate = annual_return_rate / 12 / 100
        
        # Total number of payments
        total_payments = investment_duration_years * 12
        
        # Calculate future value using SIP formula
        if monthly_rate == 0:
            # If rate is 0, FV is just sum of investments
            future_value = monthly_investment * total_payments
        else:
            # FV = P × ({[1 + r]^n - 1} / r) × (1 + r)
            future_value = monthly_investment * (
                (math.pow(1 + monthly_rate, total_payments) - 1) / monthly_rate
            ) * (1 + monthly_rate)
        
        # Calculate total invested
        total_invested = monthly_investment * total_payments
        
        # Calculate wealth generated (returns)
        wealth_generated = future_value - total_invested
        
        # Calculate yearly breakdown
        yearly_breakdown = SIPCalculator._calculate_yearly_breakdown(
            monthly_investment,
            monthly_rate,
            investment_duration_years
        )
        
        return {
            'monthly_investment': round(monthly_investment, 2),
            'annual_return_rate': annual_return_rate,
            'investment_duration_years': investment_duration_years,
            'total_invested': round(total_invested, 2),
            'wealth_generated': round(wealth_generated, 2),
            'future_value': round(future_value, 2),
            'yearly_breakdown': yearly_breakdown
        }
    
    @staticmethod
    def _calculate_yearly_breakdown(
        monthly_investment: float,
        monthly_rate: float,
        years: int
    ) -> List[Dict]:
        """
        Calculate year-wise breakdown of investments
        
        Returns list of dicts with year, invested, and value for each year
        """
        yearly_data = []
        
        for year in range(1, years + 1):
            months = year * 12
            
            # Total invested till this year
            invested = monthly_investment * months
            
            # Future value till this year
            if monthly_rate == 0:
                value = invested
            else:
                value = monthly_investment * (
                    (math.pow(1 + monthly_rate, months) - 1) / monthly_rate
                ) * (1 + monthly_rate)
            
            yearly_data.append({
                'year': year,
                'invested': round(invested, 2),
                'value': round(value, 2),
                'returns': round(value - invested, 2)
            })
        
        return yearly_data
    
    @staticmethod
    def calculate_required_sip(
        target_amount: float,
        annual_return_rate: float,
        investment_duration_years: int
    ) -> float:
        """
        Calculate required monthly SIP to achieve target amount
        
        Args:
            target_amount: Desired future value
            annual_return_rate: Expected annual return percentage
            investment_duration_years: Investment period in years
            
        Returns:
            Required monthly investment amount
        """
        monthly_rate = annual_return_rate / 12 / 100
        total_payments = investment_duration_years * 12
        
        if monthly_rate == 0:
            required_sip = target_amount / total_payments
        else:
            # Reverse SIP formula to find P
            # P = FV / ({[1 + r]^n - 1} / r) × (1 + r))
            required_sip = target_amount / (
                ((math.pow(1 + monthly_rate, total_payments) - 1) / monthly_rate) * (1 + monthly_rate)
            )
        
        return round(required_sip, 2)
