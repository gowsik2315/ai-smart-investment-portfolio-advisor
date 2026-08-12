"""
Test script for Risk Calculator
Tests the risk calculation algorithm with different profiles
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.risk_calculator import RiskCalculator


class MockFinancialProfile:
    """Mock financial profile for testing"""
    def __init__(self, age, monthly_income, monthly_savings, investment_horizon, risk_tolerance):
        self.age = age
        self.monthly_income = monthly_income
        self.monthly_savings = monthly_savings
        self.investment_horizon = investment_horizon
        self.risk_tolerance = risk_tolerance


def test_risk_calculator():
    """Test risk calculator with different profiles"""
    
    print("=" * 80)
    print("RISK PROFILING ENGINE - TEST SUITE")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "name": "Conservative Profile (Young, Low Income, Low Tolerance)",
            "profile": MockFinancialProfile(
                age=55,
                monthly_income=30000,
                monthly_savings=5000,
                investment_horizon="1-3 Years",
                risk_tolerance="Low"
            ),
            "expected_type": "Conservative"
        },
        {
            "name": "Moderate Profile (Mid-age, Medium Income, Medium Tolerance)",
            "profile": MockFinancialProfile(
                age=35,
                monthly_income=60000,
                monthly_savings=15000,
                investment_horizon="5-10 Years",
                risk_tolerance="Medium"
            ),
            "expected_type": "Moderate"
        },
        {
            "name": "Aggressive Profile (Young, High Income, High Tolerance)",
            "profile": MockFinancialProfile(
                age=25,
                monthly_income=100000,
                monthly_savings=40000,
                investment_horizon="10+ Years",
                risk_tolerance="High"
            ),
            "expected_type": "Aggressive"
        },
        {
            "name": "Edge Case - Young Conservative",
            "profile": MockFinancialProfile(
                age=22,
                monthly_income=25000,
                monthly_savings=2500,
                investment_horizon="1-3 Years",
                risk_tolerance="Low"
            ),
            "expected_type": "Conservative or Moderate"
        },
        {
            "name": "Edge Case - Old Aggressive",
            "profile": MockFinancialProfile(
                age=60,
                monthly_income=150000,
                monthly_savings=60000,
                investment_horizon="10+ Years",
                risk_tolerance="High"
            ),
            "expected_type": "Moderate or Aggressive"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 80)
        
        profile = test_case['profile']
        print(f"Input Parameters:")
        print(f"  Age: {profile.age} years")
        print(f"  Monthly Income: ₹{profile.monthly_income:,}")
        print(f"  Monthly Savings: ₹{profile.monthly_savings:,}")
        print(f"  Savings Rate: {(profile.monthly_savings/profile.monthly_income*100):.1f}%")
        print(f"  Investment Horizon: {profile.investment_horizon}")
        print(f"  Risk Tolerance: {profile.risk_tolerance}")
        
        # Calculate risk profile
        result = RiskCalculator.calculate_risk_score(profile)
        
        print(f"\nResults:")
        print(f"  Risk Score: {result['risk_score']:.2f}/100")
        print(f"  Investor Type: {result['investor_type']}")
        print(f"  Expected Type: {test_case['expected_type']}")
        
        # Check if result matches expectation
        if test_case['expected_type'] in ["Conservative", "Moderate", "Aggressive"]:
            status = "✅ PASS" if result['investor_type'] == test_case['expected_type'] else "❌ FAIL"
            print(f"  Status: {status}")
        else:
            print(f"  Status: ✅ CALCULATED")
        
        print(f"\nRecommended Allocation:")
        if result['investor_type'] == "Conservative":
            print(f"  Equity: 30% | Debt: 60% | Gold: 10%")
        elif result['investor_type'] == "Moderate":
            print(f"  Equity: 50% | Debt: 40% | Gold: 10%")
        else:
            print(f"  Equity: 70% | Debt: 20% | Gold: 10%")
        
        print(f"\nExplanation Preview:")
        explanation_lines = result['explanation'].split('\n')
        for line in explanation_lines[:5]:
            print(f"  {line}")
        print(f"  ... (truncated)")
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    test_risk_calculator()
