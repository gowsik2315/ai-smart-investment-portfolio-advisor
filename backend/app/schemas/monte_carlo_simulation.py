"""
Monte Carlo Simulation Schemas
Pydantic models for Monte Carlo portfolio simulation
"""

from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional
from datetime import datetime


# Upper bound on the annual volatility the API will accept.
#
# This was previously 1.0 (100%). That cap is fine for a hand-typed
# number but wrong for a model-predicted one: 21-day realised volatility
# for a single NSE equity clears 100% annualised in crisis windows, so a
# legitimate forecast would have been rejected with a 422 before it ever
# reached the simulator. 5.0 is a sanity ceiling, not a modelling claim.
MAX_VOLATILITY = 5.0


class MonteCarloSimulationRequest(BaseModel):
    """Request model for Monte Carlo simulation"""
    initial_investment: float = Field(..., gt=0, description="Initial investment amount")
    expected_return: float = Field(
        ..., gt=-1, le=1,
        description="Expected annual return (decimal, e.g. 0.12). Must exceed -100%."
    )
    volatility: Optional[float] = Field(
        None, ge=0, le=MAX_VOLATILITY,
        description=(
            "Annual volatility (decimal, e.g. 0.15). Optional only when "
            "use_predicted_volatility is true, in which case the forecasting "
            "service supplies it."
        )
    )
    years: int = Field(..., ge=1, le=50, description="Investment duration in years")
    num_simulations: int = Field(default=10000, ge=1000, le=50000, description="Number of simulations")
    monthly_contribution: float = Field(default=0.0, ge=0, description="Monthly contribution amount")

    # ── Volatility forecasting ───────────────────────────────────
    use_predicted_volatility: bool = Field(
        default=False,
        description=(
            "Source sigma from the volatility forecasting model instead of "
            "the supplied value. Requires `ticker`. Falls back to trailing "
            "realised volatility if no model artifact is loaded."
        )
    )
    ticker: Optional[str] = Field(
        None,
        description="Ticker to forecast volatility for, e.g. 'RELIANCE.NS'. Required when use_predicted_volatility is true."
    )

    random_seed: Optional[int] = Field(
        None,
        description=(
            "Seed for reproducible draws. Pass a fixed value when comparing a "
            "predicted sigma against a manual one, so the difference reflects "
            "the parameter rather than the random sample."
        )
    )

    simulation_name: Optional[str] = Field(None, description="Name for this simulation")
    notes: Optional[str] = Field(None, description="Notes about this simulation")

    @model_validator(mode="after")
    def validate_volatility_source(self):
        """A run needs sigma from exactly one of: the caller, or the model."""
        if not self.use_predicted_volatility and self.volatility is None:
            raise ValueError(
                "volatility is required unless use_predicted_volatility is true"
            )
        if self.use_predicted_volatility and not self.ticker:
            raise ValueError(
                "ticker is required when use_predicted_volatility is true"
            )
        return self

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
    var_5_percent: float = Field(..., description="Value at Risk (5th percentile terminal value)")
    var_loss_amount: float = Field(..., description="Shortfall vs contributions at VaR")
    var_loss_percent: float = Field(..., description="Shortfall vs contributions at VaR, percent")
    cvar_5_percent: float = Field(..., description="Conditional VaR (mean of worst 5%)")
    cvar_loss_amount: float = Field(..., description="Shortfall vs contributions at CVaR")
    cvar_loss_percent: float = Field(..., description="Shortfall vs contributions at CVaR, percent")


class VolatilityProvenance(BaseModel):
    """Where the sigma used by this simulation came from."""
    source: str = Field(..., description="'manual' | 'ml_predicted' | 'historical_fallback'")
    volatility_used: float = Field(..., description="Annual volatility actually fed to the simulator")
    predicted_volatility: Optional[float] = Field(None, description="Model forecast, if one was produced")
    model_version: Optional[str] = Field(None, description="Identifier of the model artifact used")
    ticker: Optional[str] = Field(None, description="Ticker the forecast applies to")
    fallback_reason: Optional[str] = Field(None, description="Why the forecast was not used, when applicable")


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
    risk_metrics: RiskMetrics

    # Optional
    simulation_id: Optional[int] = Field(None, description="DB id when the run was saved")
    simulation_paths: Optional[List[List[float]]] = Field(None, description="Sample simulation paths")
    volatility_provenance: Optional[VolatilityProvenance] = None
    random_seed: Optional[int] = None
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
    risk_metrics: Optional[Dict] = None
    time_periods: Optional[List[int]] = None  # Calculated field for X-axis
    volatility_source: Optional[str] = None
    predicted_volatility: Optional[float] = None
    volatility_model_version: Optional[str] = None
    volatility_ticker: Optional[str] = None
    random_seed: Optional[int] = None
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
    volatility_source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
