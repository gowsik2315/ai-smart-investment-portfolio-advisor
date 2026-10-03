"""
Transaction Model
Stores investment transactions and history
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Transaction(Base):
    """Transaction model for investment transactions"""
    
    __tablename__ = "transactions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    
    # Transaction Details
    transaction_type = Column(String, nullable=False)  # Buy, Sell, SIP, Dividend
    asset_type = Column(String, nullable=False)  # Equity, Debt, Gold, Mutual Fund
    asset_name = Column(String, nullable=False)
    asset_symbol = Column(String, nullable=True)
    
    # Financial Details
    quantity = Column(Float, nullable=True)
    price_per_unit = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    
    # Transaction Date
    transaction_date = Column(Date, nullable=False)
    
    # Additional Information
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    portfolio = relationship("Portfolio", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type}', amount={self.total_amount})>"
