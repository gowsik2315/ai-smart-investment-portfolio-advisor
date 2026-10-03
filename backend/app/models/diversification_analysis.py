"""
Diversification Analysis Model
Stores portfolio diversification analysis results
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DiversificationAnalysis(Base):
    """Diversification Analysis model for storing diversification metrics"""
    
    __tablename__ = "diversification_analyses"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Diversification Metrics
    diversification_score = Column(Float, nullable=False)  # 0-100 scale
    hhi_score = Column(Float, nullable=False)  # Herfindahl-Hirschman Index
    num_holdings = Column(Integer, nullable=False)
    total_value = Column(Float, nullable=False)
    
    # Sector Concentration (JSON)
    sector_concentration = Column(JSON, nullable=False)
    # Example: {"sectors": {"Technology": 30.5, "Banking": 25.0}, "top_sector": "Technology", ...}
    
    # Asset Concentration (JSON)
    asset_concentration = Column(JSON, nullable=False)
    # Example: {"assets": {"Stocks": 60.0, "Bonds": 30.0}, "top_asset": "Stocks", ...}
    
    # Warnings and Recommendations
    warnings = Column(JSON, nullable=True)  # List of warning messages
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    
    # Holdings Data (JSON)
    holdings_data = Column(JSON, nullable=True)  # Store holdings for reference
    
    # AI-generated explanation (cached)
    ai_explanation = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="diversification_analyses")
    
    def __repr__(self):
        return f"<DiversificationAnalysis(id={self.id}, user_id={self.user_id}, score={self.diversification_score})>"
