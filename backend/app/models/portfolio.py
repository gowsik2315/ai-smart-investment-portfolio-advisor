"""
Portfolio Model
Stores user's investment portfolio and recommendations
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Portfolio(Base):
    """Portfolio model for investment portfolios"""
    
    __tablename__ = "portfolios"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Portfolio Information
    portfolio_name = Column(String, nullable=False)
    portfolio_type = Column(String, nullable=False)  # Recommended, Custom, Current
    is_active = Column(Boolean, default=True)
    
    # Asset Allocation (JSON field to store detailed allocation)
    allocation = Column(JSON, nullable=False)
    # Example: {"equity": 60, "debt": 30, "gold": 10, "assets": [...]}
    
    # Portfolio Metrics
    total_value = Column(Float, default=0.0)
    expected_return = Column(Float, nullable=True)  # Expected annual return percentage
    risk_level = Column(String, nullable=True)  # Low, Medium, High
    
    # Performance Tracking
    current_return = Column(Float, default=0.0)  # Current return percentage
    invested_amount = Column(Float, default=0.0)
    current_amount = Column(Float, default=0.0)
    
    # Additional Information
    rebalance_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="portfolios")
    transactions = relationship("Transaction", back_populates="portfolio")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, name='{self.portfolio_name}')>"
