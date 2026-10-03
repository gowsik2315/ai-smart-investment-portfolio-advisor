"""
Financial Profile API Routes
Handles user financial profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_current_user_id
from app.models.financial_profile import FinancialProfile
from app.models.risk_profile import RiskProfile
from app.models.user import User
from app.schemas.financial_profile import FinancialProfileCreate, FinancialProfileUpdate, FinancialProfileResponse
from app.services.risk_calculator import RiskCalculator


router = APIRouter()




@router.post("/", response_model=FinancialProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_financial_profile(
    profile_data: FinancialProfileCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create financial profile for authenticated user
    
    - **age**: User age (18-100)
    - **monthly_income**: Monthly income amount
    - **monthly_savings**: Monthly savings amount
    - **investment_horizon**: Investment time horizon (1-3 Years, 3-5 Years, 5-10 Years, 10+ Years)
    - **risk_tolerance**: Risk tolerance level (Low, Medium, High)
    - **financial_goal**: Primary financial goal (Wealth Creation, Retirement, House Purchase, Education, Emergency Fund)
    """
    # Check if profile already exists
    existing_profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial profile already exists. Use PUT to update."
        )
    
    # Validate monthly savings doesn't exceed monthly income
    if profile_data.monthly_savings > profile_data.monthly_income:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monthly savings cannot exceed monthly income"
        )
    
    # Create new profile
    new_profile = FinancialProfile(
        user_id=current_user_id,
        **profile_data.model_dump()
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    # Automatically generate risk profile
    try:
        risk_data = RiskCalculator.calculate_risk_score(new_profile)
        
        risk_profile = RiskProfile(
            user_id=current_user_id,
            risk_score=risk_data['risk_score'],
            investor_type=risk_data['investor_type'],
            explanation=risk_data['explanation']
        )
        
        db.add(risk_profile)
        db.commit()
    except Exception as e:
        # Log error but don't fail profile creation
        print(f"Warning: Could not auto-generate risk profile: {e}")
    
    return new_profile


@router.get("/", response_model=FinancialProfileResponse)
async def get_financial_profile(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get financial profile for authenticated user
    """
    profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found"
        )
    
    return profile


@router.put("/", response_model=FinancialProfileResponse)
async def update_financial_profile(
    profile_data: FinancialProfileUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update financial profile for authenticated user
    
    - **profile_data**: Updated financial information (all fields optional)
    """
    profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found. Use POST to create."
        )
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    
    # Validate monthly savings doesn't exceed monthly income (if both are being set)
    new_income = update_data.get('monthly_income', profile.monthly_income)
    new_savings = update_data.get('monthly_savings', profile.monthly_savings)
    
    if new_savings > new_income:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monthly savings cannot exceed monthly income"
        )
    
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    # Recalculate risk profile
    try:
        risk_data = RiskCalculator.calculate_risk_score(profile)
        
        existing_risk_profile = db.query(RiskProfile).filter(
            RiskProfile.user_id == current_user_id
        ).first()
        
        if existing_risk_profile:
            existing_risk_profile.risk_score = risk_data['risk_score']
            existing_risk_profile.investor_type = risk_data['investor_type']
            existing_risk_profile.explanation = risk_data['explanation']
            db.commit()
        else:
            risk_profile = RiskProfile(
                user_id=current_user_id,
                risk_score=risk_data['risk_score'],
                investor_type=risk_data['investor_type'],
                explanation=risk_data['explanation']
            )
            db.add(risk_profile)
            db.commit()
    except Exception as e:
        # Log error but don't fail profile update
        print(f"Warning: Could not update risk profile: {e}")
    
    return profile


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_financial_profile(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete financial profile for authenticated user
    """
    profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found"
        )
    
    db.delete(profile)
    db.commit()
    
    return None
