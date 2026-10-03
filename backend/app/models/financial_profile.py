"""
Financial Profile Model
Stores user's financial information and background
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FinancialProfile(Base):
    """Financial profile model for user financial information"""
    
    __tablename__ = "financial_profiles"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Financial Profile Fields (as per requirements)
    age = Column(Integer, nullable=False)
    monthly_income = Column(Float, nullable=False)
    monthly_savings = Column(Float, nullable=False)
    investment_horizon = Column(String, nullable=False)  # 1-3 Years, 3-5 Years, 5-10 Years, 10+ Years
    risk_tolerance = Column(String, nullable=False)  # Low, Medium, High
    financial_goal = Column(String, nullable=False)  # Wealth Creation, Retirement, House Purchase, Education, Emergency Fund
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="financial_profile")
    
    def __repr__(self):
        return f"<FinancialProfile(user_id={self.user_id}, age={self.age}, goal='{self.financial_goal}')>"
