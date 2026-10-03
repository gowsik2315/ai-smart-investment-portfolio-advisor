"""
SIP Plan Model
Stores systematic investment plan information
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SIPPlan(Base):
    """SIP Plan model for systematic investment plans"""
    
    __tablename__ = "sip_plans"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # SIP Details
    plan_name = Column(String, nullable=False)
    investment_amount = Column(Float, nullable=False)  # Monthly investment amount
    frequency = Column(String, nullable=False)  # Monthly, Quarterly, Yearly
    
    # Duration
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    duration_months = Column(Integer, nullable=False)  # Total duration in months
    
    # Asset Allocation
    equity_percentage = Column(Float, nullable=False)
    debt_percentage = Column(Float, nullable=False)
    gold_percentage = Column(Float, default=0.0)
    
    # Projections
    expected_return_rate = Column(Float, nullable=False)  # Expected annual return percentage
    projected_corpus = Column(Float, nullable=True)  # Expected final amount
    total_investment = Column(Float, nullable=True)  # Total amount to be invested
    
    # Status
    status = Column(String, default="Active")  # Active, Completed, Paused, Cancelled
    is_active = Column(Boolean, default=True)
    
    # Progress Tracking
    installments_paid = Column(Integer, default=0)
    total_invested = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    
    # AI-generated explanation (cached)
    ai_explanation = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="sip_plans")
    
    def __repr__(self):
        return f"<SIPPlan(id={self.id}, user_id={self.user_id}, name='{self.plan_name}')>"
