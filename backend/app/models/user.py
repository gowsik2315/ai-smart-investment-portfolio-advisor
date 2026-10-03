"""
User Model
Represents authenticated users in the system
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Profile fields
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    financial_profile = relationship("FinancialProfile", back_populates="user", uselist=False)
    risk_profile = relationship("RiskProfile", back_populates="user", uselist=False)
    portfolio_recommendation = relationship("PortfolioRecommendation", back_populates="user", uselist=False)
    portfolios = relationship("Portfolio", back_populates="user")
    portfolio_analyses = relationship("PortfolioAnalysis", back_populates="user")
    diversification_analyses = relationship("DiversificationAnalysis", back_populates="user")
    monte_carlo_simulations = relationship("MonteCarloSimulation", back_populates="user")
    sip_plans = relationship("SIPPlan", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"
