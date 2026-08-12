"""
Test Script for Financial Profile Module
Verifies database setup and basic CRUD operations
"""

import sys
from sqlalchemy import inspect
from app.core.database import engine, SessionLocal
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.core.database import Base

def test_database_setup():
    """Test if database tables are created correctly"""
    print("=" * 60)
    print("Testing Financial Profile Database Setup")
    print("=" * 60)
    
    # Create all tables
    print("\n1. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Tables created successfully")
    
    # Inspect database
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n2. Checking tables...")
    required_tables = ['users', 'financial_profiles']
    for table in required_tables:
        if table in tables:
            print(f"   ✓ Table '{table}' exists")
        else:
            print(f"   ✗ Table '{table}' NOT FOUND")
            return False
    
    print("\n3. Checking 'financial_profiles' table structure...")
    columns = inspector.get_columns('financial_profiles')
    required_columns = [
        'id', 'user_id', 'age', 'monthly_income', 'monthly_savings',
        'investment_horizon', 'risk_tolerance', 'financial_goal',
        'created_at', 'updated_at'
    ]
    
    column_names = [col['name'] for col in columns]
    for col in required_columns:
        if col in column_names:
            print(f"   ✓ Column '{col}' exists")
        else:
            print(f"   ✗ Column '{col}' NOT FOUND")
            return False
    
    print("\n4. Checking foreign key constraints...")
    foreign_keys = inspector.get_foreign_keys('financial_profiles')
    if foreign_keys:
        for fk in foreign_keys:
            print(f"   ✓ Foreign key: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    else:
        print("   ⚠ No foreign keys found (may be expected for SQLite)")
    
    print("\n" + "=" * 60)
    print("Database setup verification PASSED ✓")
    print("=" * 60)
    return True


def test_crud_operations():
    """Test basic CRUD operations"""
    print("\n" + "=" * 60)
    print("Testing Financial Profile CRUD Operations")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Create a test user
        print("\n1. Creating test user...")
        test_user = User(
            email="test@example.com",
            password_hash="testpassword123",
            full_name="Test User",
            phone="1234567890"
        )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == test_user.email).first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print("   ✓ Deleted existing test user")
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"   ✓ Test user created with ID: {test_user.id}")
        
        # 2. Create financial profile
        print("\n2. Creating financial profile...")
        profile = FinancialProfile(
            user_id=test_user.id,
            age=30,
            monthly_income=75000.0,
            monthly_savings=25000.0,
            investment_horizon="5-10 Years",
            risk_tolerance="Medium",
            financial_goal="Wealth Creation"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        print(f"   ✓ Financial profile created with ID: {profile.id}")
        print(f"   ✓ Profile details:")
        print(f"      - Age: {profile.age}")
        print(f"      - Monthly Income: ₹{profile.monthly_income:,.2f}")
        print(f"      - Monthly Savings: ₹{profile.monthly_savings:,.2f}")
        print(f"      - Investment Horizon: {profile.investment_horizon}")
        print(f"      - Risk Tolerance: {profile.risk_tolerance}")
        print(f"      - Financial Goal: {profile.financial_goal}")
        
        # 3. Read financial profile
        print("\n3. Reading financial profile...")
        retrieved_profile = db.query(FinancialProfile).filter(
            FinancialProfile.user_id == test_user.id
        ).first()
        
        if retrieved_profile:
            print(f"   ✓ Profile retrieved successfully")
            print(f"   ✓ User ID: {retrieved_profile.user_id}")
            print(f"   ✓ Age: {retrieved_profile.age}")
        else:
            print("   ✗ Failed to retrieve profile")
            return False
        
        # 4. Update financial profile
        print("\n4. Updating financial profile...")
        retrieved_profile.monthly_savings = 30000.0
        retrieved_profile.risk_tolerance = "High"
        db.commit()
        db.refresh(retrieved_profile)
        print(f"   ✓ Profile updated successfully")
        print(f"   ✓ New Monthly Savings: ₹{retrieved_profile.monthly_savings:,.2f}")
        print(f"   ✓ New Risk Tolerance: {retrieved_profile.risk_tolerance}")
        
        # 5. Delete financial profile
        print("\n5. Deleting financial profile...")
        db.delete(retrieved_profile)
        db.commit()
        print("   ✓ Profile deleted successfully")
        
        # 6. Verify deletion
        print("\n6. Verifying deletion...")
        deleted_profile = db.query(FinancialProfile).filter(
            FinancialProfile.user_id == test_user.id
        ).first()
        
        if deleted_profile is None:
            print("   ✓ Profile deletion verified")
        else:
            print("   ✗ Profile still exists after deletion")
            return False
        
        # Cleanup: Delete test user
        print("\n7. Cleaning up test user...")
        db.delete(test_user)
        db.commit()
        print("   ✓ Test user deleted")
        
        print("\n" + "=" * 60)
        print("CRUD operations test PASSED ✓")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n   ✗ Error: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def test_validation():
    """Test validation constraints"""
    print("\n" + "=" * 60)
    print("Testing Validation Constraints")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create test user
        print("\n1. Creating test user for validation tests...")
        test_user = User(
            email="validation_test@example.com",
            password_hash="testpassword123",
            full_name="Validation Test User"
        )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == test_user.email).first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"   ✓ Test user created with ID: {test_user.id}")
        
        # Test unique constraint (one profile per user)
        print("\n2. Testing unique constraint (one profile per user)...")
        profile1 = FinancialProfile(
            user_id=test_user.id,
            age=25,
            monthly_income=50000.0,
            monthly_savings=15000.0,
            investment_horizon="3-5 Years",
            risk_tolerance="Low",
            financial_goal="Emergency Fund"
        )
        db.add(profile1)
        db.commit()
        print("   ✓ First profile created")
        
        # Try to create second profile for same user (should fail)
        try:
            profile2 = FinancialProfile(
                user_id=test_user.id,
                age=26,
                monthly_income=55000.0,
                monthly_savings=16000.0,
                investment_horizon="5-10 Years",
                risk_tolerance="Medium",
                financial_goal="Wealth Creation"
            )
            db.add(profile2)
            db.commit()
            print("   ✗ Second profile created (should have failed)")
            return False
        except Exception as e:
            db.rollback()
            print("   ✓ Unique constraint working (second profile rejected)")
        
        # Cleanup
        print("\n3. Cleaning up test data...")
        db.delete(profile1)
        db.delete(test_user)
        db.commit()
        print("   ✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("Validation test PASSED ✓")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n   ✗ Error: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🧪 FINANCIAL PROFILE MODULE TEST SUITE")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_database_setup()
    
    if test1_passed:
        test2_passed = test_crud_operations()
        test3_passed = test_validation()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Database Setup:       {'✓ PASSED' if test1_passed else '✗ FAILED'}")
        print(f"CRUD Operations:      {'✓ PASSED' if test2_passed else '✗ FAILED'}")
        print(f"Validation:           {'✓ PASSED' if test3_passed else '✗ FAILED'}")
        print("=" * 60)
        
        if test1_passed and test2_passed and test3_passed:
            print("\n🎉 All tests PASSED! Financial Profile module is ready.")
            sys.exit(0)
        else:
            print("\n❌ Some tests FAILED. Please review the errors above.")
            sys.exit(1)
    else:
        print("\n❌ Database setup failed. Cannot proceed with other tests.")
        sys.exit(1)
