"""
Database Initialization Script
Run this script to initialize the database with tables
"""

from app.core.database import engine, Base
from app.models import User, FinancialProfile, RiskProfile, Portfolio, SIPPlan, Transaction


def init_db():
    """Initialize database tables"""
    print("🔧 Initializing database...")
    print(f"📍 Database URL: {engine.url}")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - financial_profiles")
        print("  - risk_profiles")
        print("  - portfolios")
        print("  - sip_plans")
        print("  - transactions")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    init_db()
