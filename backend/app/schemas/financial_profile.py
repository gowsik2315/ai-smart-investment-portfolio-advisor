"""
Financial Profile Schemas
Pydantic models for financial profile requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class FinancialProfileBase(BaseModel):
    """Base financial profile schema"""
    age: int = Field(..., ge=18, le=100, description="User age (18-100)")
    monthly_income: float = Field(..., gt=0, description="Monthly income in currency")
    monthly_savings: float = Field(..., ge=0, description="Monthly savings amount")
    investment_horizon: str = Field(..., description="Investment time horizon")
    risk_tolerance: str = Field(..., description="Risk tolerance level")
    financial_goal: str = Field(..., description="Primary financial goal")
    
    @validator('investment_horizon')
    def validate_investment_horizon(cls, v):
        allowed_horizons = ['1-3 Years', '3-5 Years', '5-10 Years', '10+ Years']
        if v not in allowed_horizons:
            raise ValueError(f'Investment horizon must be one of: {", ".join(allowed_horizons)}')
        return v
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        allowed_risks = ['Low', 'Medium', 'High']
        if v not in allowed_risks:
            raise ValueError(f'Risk tolerance must be one of: {", ".join(allowed_risks)}')
        return v
    
    @validator('financial_goal')
    def validate_financial_goal(cls, v):
        allowed_goals = ['Wealth Creation', 'Retirement', 'House Purchase', 'Education', 'Emergency Fund']
        if v not in allowed_goals:
            raise ValueError(f'Financial goal must be one of: {", ".join(allowed_goals)}')
        return v


class FinancialProfileCreate(FinancialProfileBase):
    """Schema for creating financial profile"""
    pass


class FinancialProfileUpdate(BaseModel):
    """Schema for updating financial profile"""
    age: Optional[int] = Field(None, ge=18, le=100)
    monthly_income: Optional[float] = Field(None, gt=0)
    monthly_savings: Optional[float] = Field(None, ge=0)
    investment_horizon: Optional[str] = None
    risk_tolerance: Optional[str] = None
    financial_goal: Optional[str] = None
    
    @validator('investment_horizon')
    def validate_investment_horizon(cls, v):
        if v is not None:
            allowed_horizons = ['1-3 Years', '3-5 Years', '5-10 Years', '10+ Years']
            if v not in allowed_horizons:
                raise ValueError(f'Investment horizon must be one of: {", ".join(allowed_horizons)}')
        return v
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        if v is not None:
            allowed_risks = ['Low', 'Medium', 'High']
            if v not in allowed_risks:
                raise ValueError(f'Risk tolerance must be one of: {", ".join(allowed_risks)}')
        return v
    
    @validator('financial_goal')
    def validate_financial_goal(cls, v):
        if v is not None:
            allowed_goals = ['Wealth Creation', 'Retirement', 'House Purchase', 'Education', 'Emergency Fund']
            if v not in allowed_goals:
                raise ValueError(f'Financial goal must be one of: {", ".join(allowed_goals)}')
        return v


class FinancialProfileResponse(FinancialProfileBase):
    """Schema for financial profile response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
