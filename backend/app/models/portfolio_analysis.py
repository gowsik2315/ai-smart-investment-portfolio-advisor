"""
Portfolio Analysis Model
Stores portfolio risk analysis results
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PortfolioAnalysis(Base):
    """Portfolio Analysis model for storing risk metrics"""
    
    __tablename__ = "portfolio_analyses"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Risk Metrics
    volatility = Column(Float, nullable=False)  # Annualized volatility (decimal)
    volatility_percent = Column(Float, nullable=False)  # Volatility as percentage
    sharpe_ratio = Column(Float, nullable=False)  # Risk-adjusted return metric
    max_drawdown = Column(Float, nullable=False)  # Maximum drawdown (decimal)
    max_drawdown_percent = Column(Float, nullable=False)  # Max drawdown as percentage
    risk_score = Column(Float, nullable=False)  # Overall risk score (0-100)
    risk_level = Column(String, nullable=False)  # Low, Moderate, High, Very High
    
    # Performance Metrics
    average_return = Column(Float, nullable=True)  # Annualized average return (decimal)
    average_return_percent = Column(Float, nullable=True)  # Average return as percentage
    total_return = Column(Float, nullable=True)  # Total return percentage
    
    # Analysis Metadata
    risk_free_rate = Column(Float, nullable=False)  # Risk-free rate used
    data_points = Column(Integer, nullable=False)  # Number of data points analyzed
    analysis_period_days = Column(Integer, nullable=False)  # Analysis period in days
    
    # Portfolio Data (JSON)
    portfolio_data = Column(JSON, nullable=True)  # Store historical data for reference
    
    # AI-generated explanation (cached)
    ai_explanation = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="portfolio_analyses")
    
    def __repr__(self):
        return f"<PortfolioAnalysis(id={self.id}, user_id={self.user_id}, risk_level='{self.risk_level}')>"
