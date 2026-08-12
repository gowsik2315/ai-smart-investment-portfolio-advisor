"""
SIP Plan Schemas
Pydantic models for SIP plan operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date


class SIPCalculationRequest(BaseModel):
    """Schema for SIP calculation request"""
    monthly_investment: float = Field(..., gt=0, description="Monthly investment amount")
    annual_return_rate: float = Field(..., ge=0, le=100, description="Expected annual return percentage")
    investment_duration_years: int = Field(..., gt=0, le=50, description="Investment duration in years")


class YearlyBreakdown(BaseModel):
    """Schema for yearly breakdown data"""
    year: int
    invested: float
    value: float
    returns: float


class SIPCalculationResponse(BaseModel):
    """Schema for SIP calculation response"""
    monthly_investment: float
    annual_return_rate: float
    investment_duration_years: int
    total_invested: float
    wealth_generated: float
    future_value: float
    yearly_breakdown: List[YearlyBreakdown]
    ai_explanation: Optional[str] = Field(None, description="AI-generated explanation (cached)")


class SIPPlanBase(BaseModel):
    """Base SIP plan schema"""
    plan_name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    investment_amount: float = Field(..., gt=0, description="Monthly investment amount")
    frequency: str = Field(default="Monthly", description="Investment frequency")
    start_date: date = Field(..., description="Plan start date")
    duration_months: int = Field(..., gt=0, description="Duration in months")
    equity_percentage: float = Field(..., ge=0, le=100)
    debt_percentage: float = Field(..., ge=0, le=100)
    gold_percentage: float = Field(default=0.0, ge=0, le=100)
    expected_return_rate: float = Field(..., ge=0, le=100, description="Expected annual return %")
    
    @validator('frequency')
    def validate_frequency(cls, v):
        allowed = ['Monthly', 'Quarterly', 'Yearly']
        if v not in allowed:
            raise ValueError(f'Frequency must be one of {allowed}')
        return v


class SIPPlanCreate(SIPPlanBase):
    """Schema for creating SIP plan"""
    pass


class SIPPlanUpdate(BaseModel):
    """Schema for updating SIP plan"""
    plan_name: Optional[str] = Field(None, min_length=1, max_length=100)
    investment_amount: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None
    is_active: Optional[bool] = None
    expected_return_rate: Optional[float] = Field(None, ge=0, le=100)


class SIPPlanResponse(SIPPlanBase):
    """Schema for SIP plan response"""
    id: int
    user_id: int
    end_date: Optional[date]
    projected_corpus: Optional[float]
    total_investment: Optional[float]
    status: str
    is_active: bool
    installments_paid: int
    total_invested: float
    current_value: float
    ai_explanation: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
