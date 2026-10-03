"""
Monte Carlo Simulation Model
Stores portfolio simulation results
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MonteCarloSimulation(Base):
    """Monte Carlo Simulation model for storing simulation results"""
    
    __tablename__ = "monte_carlo_simulations"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Simulation Parameters
    initial_investment = Column(Float, nullable=False)
    expected_return = Column(Float, nullable=False)  # Annual return (decimal)
    volatility = Column(Float, nullable=False)  # Annual volatility (decimal) actually used
    years = Column(Integer, nullable=False)
    num_simulations = Column(Integer, nullable=False, default=10000)
    monthly_contribution = Column(Float, nullable=False, default=0.0)

    # Provenance of the volatility input.
    # Records whether sigma was typed by the user, produced by the
    # volatility forecasting model, or fell back to trailing realised
    # volatility because the model was unavailable. Without this the
    # stored rows cannot distinguish an ML-driven run from a manual one.
    volatility_source = Column(String, nullable=False, default="manual")
    # 'manual' | 'ml_predicted' | 'historical_fallback'

    # What the model forecast, retained even when the user overrides it,
    # so predicted-vs-used can be compared after the fact.
    predicted_volatility = Column(Float, nullable=True)

    # Identifier of the model artifact behind `predicted_volatility`
    volatility_model_version = Column(String, nullable=True)

    # Ticker the forecast was made for, when applicable
    volatility_ticker = Column(String, nullable=True)

    # Seed used for the draws; lets a stored run be reproduced exactly
    random_seed = Column(Integer, nullable=True)
    
    # Simulation Results - Statistics (JSON)
    statistics = Column(JSON, nullable=False)
    # Example: {"mean_value": 150000, "median_value": 145000, ...}
    
    # Scenarios (JSON)
    scenarios = Column(JSON, nullable=False)
    # Example: {"best_case": 200000, "average_case": 150000, "worst_case": 100000}
    
    # Confidence Intervals (JSON)
    confidence_intervals = Column(JSON, nullable=False)
    # Example: {"ci_90": {"lower": 120000, "upper": 180000}, ...}
    
    # Percentile Paths for charting (JSON)
    percentile_paths = Column(JSON, nullable=True)
    # Example: {"p10": [...], "p50": [...], "p90": [...]}
    
    # Histogram Data (JSON)
    histogram_data = Column(JSON, nullable=True)
    # Example: {"bins": [...], "frequencies": [...], "percentages": [...]}
    
    # Risk Metrics (JSON) - Optional
    risk_metrics = Column(JSON, nullable=True)
    # Example: {"var_5_percent": 95000, "cvar_5_percent": 90000, ...}
    
    # User Notes
    simulation_name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # AI-generated explanation (cached)
    ai_explanation = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="monte_carlo_simulations")
    
    def __repr__(self):
        return f"<MonteCarloSimulation(id={self.id}, user_id={self.user_id}, years={self.years})>"
