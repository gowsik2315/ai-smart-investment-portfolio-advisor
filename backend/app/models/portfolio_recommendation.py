"""
Portfolio Recommendation Model
Stores automated portfolio allocation recommendations based on risk profile
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PortfolioRecommendation(Base):
    """Portfolio recommendation model for asset allocation"""
    
    __tablename__ = "portfolio_recommendations"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Allocation Percentages
    stocks_percent = Column(Float, nullable=False)  # Stock allocation percentage
    mutual_funds_percent = Column(Float, nullable=False)  # Mutual funds allocation
    gold_percent = Column(Float, nullable=False)  # Gold allocation
    emergency_percent = Column(Float, nullable=False)  # Emergency fund allocation
    
    # Additional Information
    recommendation_summary = Column(Text, nullable=True)  # Summary explanation
    
    # AI-generated explanation (cached)
    ai_explanation = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="portfolio_recommendation")
    
    def __repr__(self):
        return f"<PortfolioRecommendation(user_id={self.user_id}, stocks={self.stocks_percent}%, mf={self.mutual_funds_percent}%)>"
