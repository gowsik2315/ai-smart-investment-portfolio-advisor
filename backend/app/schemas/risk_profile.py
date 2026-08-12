"""
Risk Profile Schemas
Pydantic models for automated risk assessment
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RiskProfileBase(BaseModel):
    """Base risk profile schema"""
    risk_score: float = Field(..., ge=0, le=100, description="Calculated risk score (0-100)")
    investor_type: str = Field(..., pattern="^(Conservative|Moderate|Aggressive)$", description="Investor classification")
    explanation: Optional[str] = Field(None, description="Explanation of risk calculation")
    ai_explanation: Optional[str] = Field(None, description="AI-generated explanation (cached)")


class RiskProfileCreate(RiskProfileBase):
    """Schema for creating risk profile"""
    pass


class RiskProfileResponse(RiskProfileBase):
    """Schema for risk profile response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
