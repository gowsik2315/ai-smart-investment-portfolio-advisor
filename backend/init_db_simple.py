"""Simple database initialization script"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.database import engine, Base
    from app.models import User, FinancialProfile, RiskProfile, Portfolio, SIPPlan, Transaction
    
    print("🔧 Initializing database...")
    print(f"📍 Database URL: {engine.url}")
    
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
    print("\n🎉 Database initialization complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
