"""
Monte Carlo Simulation Schemas
Pydantic models for Monte Carlo portfolio simulation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class MonteCarloSimulationRequest(BaseModel):
    """Request model for Monte Carlo simulation"""
    initial_investment: float = Field(..., gt=0, description="Initial investment amount")
    expected_return: float = Field(..., ge=-1, le=1, description="Expected annual return (decimal, e.g., 0.12)")
    volatility: float = Field(..., ge=0, le=1, description="Annual volatility (decimal, e.g., 0.15)")
    years: int = Field(..., ge=1, le=50, description="Investment duration in years")
    num_simulations: int = Field(default=10000, ge=1000, le=50000, description="Number of simulations")
    monthly_contribution: float = Field(default=0.0, ge=0, description="Monthly contribution amount")
    simulation_name: Optional[str] = Field(None, description="Name for this simulation")
    notes: Optional[str] = Field(None, description="Notes about this simulation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "initial_investment": 100000,
                "expected_return": 0.12,
                "volatility": 0.15,
                "years": 10,
                "num_simulations": 10000,
                "monthly_contribution": 5000,
                "simulation_name": "Retirement Portfolio 2035",
                "notes": "Conservative growth strategy"
            }
        }


class Statistics(BaseModel):
    """Statistical metrics from simulation"""
    mean_value: float
    median_value: float
    std_deviation: float
    min_value: float
    max_value: float
    mean_return_percent: float
    median_return_percent: float
    probability_of_profit: float
    probability_of_doubling: float
    probability_of_loss: float
    total_contributions: float


class Scenarios(BaseModel):
    """Best, average, and worst case scenarios"""
    best_case: float = Field(..., description="95th percentile outcome")
    average_case: float = Field(..., description="50th percentile (median) outcome")
    worst_case: float = Field(..., description="5th percentile outcome")


class ConfidenceIntervalRange(BaseModel):
    """Confidence interval range"""
    lower: float
    upper: float


class ConfidenceIntervals(BaseModel):
    """Confidence intervals at different levels"""
    ci_90: ConfidenceIntervalRange = Field(..., description="90% confidence interval")
    ci_95: ConfidenceIntervalRange = Field(..., description="95% confidence interval")
    ci_99: ConfidenceIntervalRange = Field(..., description="99% confidence interval")


class HistogramData(BaseModel):
    """Histogram data for distribution chart"""
    bins: List[float] = Field(..., description="Bin centers")
    frequencies: List[int] = Field(..., description="Frequency counts")
    percentages: List[float] = Field(..., description="Percentage frequencies")


class PercentilePaths(BaseModel):
    """Percentile paths over time"""
    p10: List[float] = Field(..., description="10th percentile path")
    p25: List[float] = Field(..., description="25th percentile path")
    p50: List[float] = Field(..., description="50th percentile (median) path")
    p75: List[float] = Field(..., description="75th percentile path")
    p90: List[float] = Field(..., description="90th percentile path")


class RiskMetrics(BaseModel):
    """Risk metrics from simulation"""
    var_5_percent: float = Field(..., description="Value at Risk (5th percentile)")
    var_loss_amount: float = Field(..., description="Potential loss amount at VaR")
    var_loss_percent: float = Field(..., description="Potential loss percentage at VaR")
    cvar_5_percent: float = Field(..., description="Conditional VaR (average of worst 5%)")
    cvar_loss_amount: float = Field(..., description="Potential loss amount at CVaR")
    cvar_loss_percent: float = Field(..., description="Potential loss percentage at CVaR")


class MonteCarloSimulationResponse(BaseModel):
    """Response model with simulation results"""
    # Simulation Parameters
    initial_investment: float
    expected_return: float
    volatility: float
    years: int
    num_simulations: int
    monthly_contribution: float
    
    # Results
    statistics: Statistics
    scenarios: Scenarios
    confidence_intervals: ConfidenceIntervals
    histogram_data: HistogramData
    percentile_paths: PercentilePaths
    time_periods: List[int]
    
    # Optional
    simulation_paths: Optional[List[List[float]]] = Field(None, description="Sample simulation paths")
    risk_metrics: Optional[RiskMetrics] = None
    ai_explanation: Optional[str] = Field(None, description="AI-generated explanation (cached)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "initial_investment": 100000,
                "expected_return": 0.12,
                "volatility": 0.15,
                "years": 10,
                "num_simulations": 10000,
                "monthly_contribution": 5000,
                "statistics": {
                    "mean_value": 950000,
                    "median_value": 920000,
                    "std_deviation": 180000,
                    "probability_of_profit": 85.5
                },
                "scenarios": {
                    "best_case": 1200000,
                    "average_case": 920000,
                    "worst_case": 650000
                }
            }
        }


class MonteCarloSimulationDB(BaseModel):
    """Database model response"""
    id: int
    user_id: int
    initial_investment: float
    expected_return: float
    volatility: float
    years: int
    num_simulations: int
    monthly_contribution: float
    statistics: Dict
    scenarios: Dict
    confidence_intervals: Dict
    percentile_paths: Optional[Dict] = None  # Added for graph persistence
    histogram_data: Optional[Dict] = None     # Added for graph persistence
    time_periods: Optional[List[int]] = None  # Calculated field for X-axis
    simulation_name: Optional[str]
    notes: Optional[str]
    ai_explanation: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SimulationSummary(BaseModel):
    """Summary model for listing simulations"""
    id: int
    simulation_name: Optional[str]
    initial_investment: float
    years: int
    num_simulations: int
    average_case: float
    created_at: datetime
    
    class Config:
        from_attributes = True
