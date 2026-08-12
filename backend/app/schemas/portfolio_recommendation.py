"""
Portfolio Recommendation Schemas
Pydantic models for portfolio allocation recommendations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class PortfolioRecommendationBase(BaseModel):
    """Base portfolio recommendation schema"""
    stocks_percent: float = Field(..., ge=0, le=100, description="Stock allocation percentage")
    mutual_funds_percent: float = Field(..., ge=0, le=100, description="Mutual funds allocation percentage")
    gold_percent: float = Field(..., ge=0, le=100, description="Gold allocation percentage")
    emergency_percent: float = Field(..., ge=0, le=100, description="Emergency fund allocation percentage")
    recommendation_summary: Optional[str] = Field(None, description="Summary explanation of recommendation")
    ai_explanation: Optional[str] = Field(None, description="AI-generated explanation (cached)")
    
    @validator('stocks_percent', 'mutual_funds_percent', 'gold_percent', 'emergency_percent')
    def validate_percentage(cls, v):
        """Ensure percentage is between 0 and 100"""
        if not 0 <= v <= 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v


class PortfolioRecommendationCreate(PortfolioRecommendationBase):
    """Schema for creating portfolio recommendation"""
    pass


class PortfolioRecommendationResponse(PortfolioRecommendationBase):
    """Schema for portfolio recommendation response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
