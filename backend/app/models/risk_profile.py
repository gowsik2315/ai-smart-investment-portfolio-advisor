"""
Risk Profile Model
Stores user's automatically calculated risk assessment
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RiskProfile(Base):
    """Risk profile model for automated risk assessment"""
    
    __tablename__ = "risk_profiles"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Risk Assessment Results
    risk_score = Column(Float, nullable=False)  # Calculated risk score (0-100)
    investor_type = Column(String, nullable=False)  # Conservative, Moderate, Aggressive
    
    # Calculation explanation
    explanation = Column(Text, nullable=True)
    
    # AI-generated explanation (cached)
    ai_explanation = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="risk_profile")
    
    def __repr__(self):
        return f"<RiskProfile(user_id={self.user_id}, investor_type='{self.investor_type}', score={self.risk_score})>"
