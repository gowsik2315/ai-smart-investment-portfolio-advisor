"""
Portfolio Analysis Schemas
Pydantic models for portfolio risk analysis
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class PortfolioDataPoint(BaseModel):
    """Portfolio data point for analysis"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    value: float = Field(..., gt=0, description="Portfolio value on this date")


class PortfolioAnalysisRequest(BaseModel):
    """Request model for portfolio analysis"""
    portfolio_data: List[PortfolioDataPoint] = Field(
        ..., 
        min_items=2,
        description="Historical portfolio values (at least 2 data points required)"
    )
    risk_free_rate: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Annual risk-free rate (default: 0.06 or 6%)"
    )


class RiskInterpretation(BaseModel):
    """Risk level interpretation and recommendations"""
    description: str
    characteristics: List[str]
    recommendations: List[str]


class PortfolioAnalysisResponse(BaseModel):
    """Response model with analysis results"""
    # Risk Metrics
    volatility: float = Field(..., description="Annualized volatility (decimal)")
    volatility_percent: float = Field(..., description="Volatility as percentage")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown (decimal)")
    max_drawdown_percent: float = Field(..., description="Max drawdown as percentage")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")
    risk_level: str = Field(..., description="Risk level classification")
    
    # Performance Metrics
    average_return: float = Field(..., description="Annualized average return (decimal)")
    average_return_percent: float = Field(..., description="Average return as percentage")
    total_return: float = Field(..., description="Total return percentage")
    
    # Analysis Metadata
    risk_free_rate: float = Field(..., description="Risk-free rate used")
    data_points: int = Field(..., description="Number of data points analyzed")
    analysis_period_days: int = Field(..., description="Analysis period in days")
    
    # Interpretation
    interpretation: RiskInterpretation = Field(..., description="Risk interpretation and recommendations")
    ai_explanation: Optional[str] = Field(None, description="AI-generated explanation (cached)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "volatility": 0.1523,
                "volatility_percent": 15.23,
                "sharpe_ratio": 1.2456,
                "max_drawdown": -0.1234,
                "max_drawdown_percent": -12.34,
                "risk_score": 45.67,
                "risk_level": "Moderate",
                "average_return": 0.0987,
                "average_return_percent": 9.87,
                "total_return": 12.34,
                "risk_free_rate": 0.06,
                "data_points": 252,
                "analysis_period_days": 252,
                "interpretation": {
                    "description": "Your portfolio exhibits moderate risk...",
                    "characteristics": ["Moderate volatility..."],
                    "recommendations": ["Continue monitoring..."]
                }
            }
        }


class PortfolioAnalysisDB(BaseModel):
    """Database model response"""
    id: int
    user_id: int
    volatility: float
    volatility_percent: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    risk_score: float
    risk_level: str
    average_return: Optional[float]
    average_return_percent: Optional[float]
    total_return: Optional[float]
    risk_free_rate: float
    data_points: int
    analysis_period_days: int
    ai_explanation: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GenerateSampleDataRequest(BaseModel):
    """Request model for generating sample data"""
    initial_value: float = Field(default=100000, gt=0, description="Initial portfolio value")
    days: int = Field(default=252, ge=30, le=1260, description="Number of days (30-1260)")
    volatility: float = Field(default=0.15, ge=0, le=1, description="Annual volatility (0-1)")
    drift: float = Field(default=0.10, ge=-1, le=1, description="Annual return/drift (-1 to 1)")
