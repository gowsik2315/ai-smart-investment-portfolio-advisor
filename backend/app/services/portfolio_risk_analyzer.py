"""
Portfolio Risk Analysis Service
Calculates portfolio risk metrics including volatility, Sharpe ratio, and maximum drawdown
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class PortfolioRiskAnalyzer:
    """
    Analyzes portfolio risk using various financial metrics
    """
    
    # Risk-free rate (annual) - using typical T-Bill rate
    RISK_FREE_RATE = 0.06  # 6%
    
    @staticmethod
    def calculate_portfolio_risk(
        portfolio_data: List[Dict],
        risk_free_rate: Optional[float] = None
    ) -> Dict:
        """
        Calculate comprehensive portfolio risk metrics
        
        Args:
            portfolio_data: List of daily portfolio values
                [{date, value}, ...]
            risk_free_rate: Annual risk-free rate (default: 6%)
            
        Returns:
            dict with volatility, sharpe_ratio, max_drawdown, risk_score, etc.
        """
        if not portfolio_data or len(portfolio_data) < 2:
            raise ValueError("Insufficient data for risk analysis. Need at least 2 data points.")
        
        # Extract values and calculate returns
        values = [point['value'] for point in portfolio_data]
        returns = PortfolioRiskAnalyzer._calculate_returns(values)
        
        if len(returns) == 0:
            raise ValueError("Cannot calculate returns from provided data.")
        
        # Use provided risk-free rate or default
        rf_rate = risk_free_rate if risk_free_rate is not None else PortfolioRiskAnalyzer.RISK_FREE_RATE
        
        # Calculate metrics
        volatility = PortfolioRiskAnalyzer._calculate_volatility(returns)
        sharpe_ratio = PortfolioRiskAnalyzer._calculate_sharpe_ratio(returns, rf_rate)
        max_drawdown = PortfolioRiskAnalyzer._calculate_max_drawdown(values)
        
        # Calculate additional metrics
        avg_return = np.mean(returns) * 252  # Annualized
        total_return = ((values[-1] - values[0]) / values[0]) * 100
        
        # Calculate risk score (0-100 scale)
        risk_score = PortfolioRiskAnalyzer._calculate_risk_score(
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown
        )
        
        # Risk classification
        risk_level = PortfolioRiskAnalyzer._classify_risk_level(risk_score)
        
        return {
            'volatility': round(volatility, 4),
            'volatility_percent': round(volatility * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 4),
            'max_drawdown': round(max_drawdown, 4),
            'max_drawdown_percent': round(max_drawdown * 100, 2),
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'average_return': round(avg_return, 4),
            'average_return_percent': round(avg_return * 100, 2),
            'total_return': round(total_return, 2),
            'risk_free_rate': rf_rate,
            'data_points': len(portfolio_data),
            'analysis_period_days': len(portfolio_data),
        }
    
    @staticmethod
    def _calculate_returns(values: List[float]) -> np.ndarray:
        """
        Calculate daily returns from portfolio values
        
        Returns: Array of daily returns
        """
        values_array = np.array(values)
        returns = np.diff(values_array) / values_array[:-1]
        return returns
    
    @staticmethod
    def _calculate_volatility(returns: np.ndarray) -> float:
        """
        Calculate annualized volatility (standard deviation of returns)
        
        Formula: σ = std(returns) × √252
        where 252 is the number of trading days in a year
        
        Returns: Annualized volatility
        """
        daily_volatility = np.std(returns, ddof=1)
        annualized_volatility = daily_volatility * np.sqrt(252)
        return float(annualized_volatility)
    
    @staticmethod
    def _calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float) -> float:
        """
        Calculate Sharpe Ratio
        
        Formula: (Average Return - Risk Free Rate) / Volatility
        
        Higher Sharpe ratio indicates better risk-adjusted returns
        - > 1.0: Good
        - > 2.0: Very good
        - > 3.0: Excellent
        
        Returns: Sharpe ratio
        """
        # Annualize returns
        avg_return = np.mean(returns) * 252
        volatility = np.std(returns, ddof=1) * np.sqrt(252)
        
        if volatility == 0:
            return 0.0
        
        sharpe_ratio = (avg_return - risk_free_rate) / volatility
        return float(sharpe_ratio)
    
    @staticmethod
    def _calculate_max_drawdown(values: List[float]) -> float:
        """
        Calculate maximum drawdown
        
        Maximum drawdown is the largest peak-to-trough decline
        
        Formula: (Trough Value - Peak Value) / Peak Value
        
        Returns: Maximum drawdown as decimal (negative value)
        """
        values_array = np.array(values)
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(values_array)
        
        # Calculate drawdown at each point
        drawdown = (values_array - running_max) / running_max
        
        # Maximum drawdown is the most negative value
        max_drawdown = float(np.min(drawdown))
        
        return max_drawdown
    
    @staticmethod
    def _calculate_risk_score(
        volatility: float,
        sharpe_ratio: float,
        max_drawdown: float
    ) -> float:
        """
        Calculate overall risk score (0-100)
        
        Lower score = Lower risk
        Higher score = Higher risk
        
        Weights:
        - Volatility: 40%
        - Sharpe Ratio: 30%
        - Max Drawdown: 30%
        """
        # Volatility score (0-100)
        # Low volatility (< 10%) = Low score
        # High volatility (> 40%) = High score
        vol_score = min(100, (volatility / 0.4) * 100)
        
        # Sharpe ratio score (inverted - higher Sharpe = lower risk)
        # Sharpe < 0: High risk (score 100)
        # Sharpe > 3: Low risk (score 0)
        if sharpe_ratio < 0:
            sharpe_score = 100
        elif sharpe_ratio > 3:
            sharpe_score = 0
        else:
            sharpe_score = 100 - (sharpe_ratio / 3) * 100
        
        # Max drawdown score
        # Small drawdown (> -10%) = Low score
        # Large drawdown (< -50%) = High score
        abs_drawdown = abs(max_drawdown)
        dd_score = min(100, (abs_drawdown / 0.5) * 100)
        
        # Weighted average
        risk_score = (vol_score * 0.4) + (sharpe_score * 0.3) + (dd_score * 0.3)
        
        return risk_score
    
    @staticmethod
    def _classify_risk_level(risk_score: float) -> str:
        """
        Classify risk level based on risk score
        
        Returns: "Low", "Moderate", "High", or "Very High"
        """
        if risk_score < 30:
            return "Low"
        elif risk_score < 50:
            return "Moderate"
        elif risk_score < 70:
            return "High"
        else:
            return "Very High"
    
    @staticmethod
    def generate_sample_portfolio_data(
        initial_value: float = 100000,
        days: int = 252,
        volatility: float = 0.15,
        drift: float = 0.10
    ) -> List[Dict]:
        """
        Generate sample portfolio data for testing
        Uses geometric Brownian motion
        
        Args:
            initial_value: Starting portfolio value
            days: Number of days to simulate
            volatility: Annual volatility
            drift: Annual return (drift)
            
        Returns:
            List of {date, value} dicts
        """
        # Don't set seed - allow random variation
        # np.random.seed(42)  
        
        # Daily parameters
        dt = 1/252
        drift_daily = drift * dt
        vol_daily = volatility * np.sqrt(dt)
        
        # Generate random returns
        returns = np.random.normal(drift_daily, vol_daily, days)
        
        # Calculate cumulative returns
        price_path = initial_value * np.exp(np.cumsum(returns))
        
        # Create data points
        start_date = datetime.now() - timedelta(days=days)
        portfolio_data = []
        
        for i, value in enumerate(price_path):
            date = start_date + timedelta(days=i)
            portfolio_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': round(float(value), 2)
            })
        
        return portfolio_data
    
    @staticmethod
    def get_risk_interpretation(risk_level: str) -> Dict:
        """
        Get interpretation and recommendations for risk level
        
        Returns: dict with interpretation and recommendations
        """
        interpretations = {
            "Low": {
                "description": "Your portfolio shows low risk characteristics with stable returns and minimal volatility.",
                "characteristics": [
                    "Low volatility and stable price movements",
                    "Good risk-adjusted returns (Sharpe ratio)",
                    "Minimal drawdowns during market downturns"
                ],
                "recommendations": [
                    "Consider increasing equity allocation for higher growth potential",
                    "Your conservative approach provides stability",
                    "Suitable for near-term goals or risk-averse investors"
                ]
            },
            "Moderate": {
                "description": "Your portfolio exhibits moderate risk with balanced risk-return characteristics.",
                "characteristics": [
                    "Moderate volatility with reasonable fluctuations",
                    "Balanced risk-adjusted returns",
                    "Manageable drawdowns within acceptable range"
                ],
                "recommendations": [
                    "Well-balanced portfolio suitable for most investors",
                    "Continue monitoring and rebalancing periodically",
                    "Good for medium to long-term investment goals"
                ]
            },
            "High": {
                "description": "Your portfolio shows elevated risk levels with significant volatility.",
                "characteristics": [
                    "High volatility with substantial price swings",
                    "Risk-return balance may need attention",
                    "Notable drawdowns during market stress"
                ],
                "recommendations": [
                    "Consider diversifying to reduce concentration risk",
                    "Review asset allocation and rebalance if needed",
                    "Ensure alignment with your risk tolerance",
                    "Monitor portfolio more frequently"
                ]
            },
            "Very High": {
                "description": "Your portfolio exhibits very high risk with extreme volatility and drawdowns.",
                "characteristics": [
                    "Very high volatility and unpredictable movements",
                    "Poor risk-adjusted returns",
                    "Severe drawdowns that may impact financial goals"
                ],
                "recommendations": [
                    "Immediate rebalancing recommended",
                    "Significantly reduce concentration in high-risk assets",
                    "Increase allocation to stable assets",
                    "Consult with a financial advisor",
                    "Not suitable for conservative investors or near-term goals"
                ]
            }
        }
        
        return interpretations.get(risk_level, interpretations["Moderate"])
