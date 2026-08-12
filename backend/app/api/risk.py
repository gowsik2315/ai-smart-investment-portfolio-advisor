"""
Risk Assessment API Routes
Handles automated risk profiling based on financial profile
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.risk_profile import RiskProfile
from app.models.financial_profile import FinancialProfile
from app.models.user import User
from app.schemas.risk_profile import RiskProfileResponse
from app.services.risk_calculator import RiskCalculator
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts


router = APIRouter()


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> int:
    """
    Dependency to get current user from JWT token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = get_current_user_id(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_id


@router.post("/calculate", response_model=RiskProfileResponse, status_code=status.HTTP_201_CREATED)
async def calculate_risk_profile(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate risk profile automatically from financial profile
    
    Requires financial profile to exist.
    Generates risk score based on:
    - Age
    - Income
    - Savings
    - Investment Horizon
    - Risk Tolerance
    
    Returns risk score (0-100) and investor type classification
    """
    # Get financial profile
    financial_profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    if not financial_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found. Please create your financial profile first."
        )
    
    # Calculate risk score
    risk_data = RiskCalculator.calculate_risk_score(financial_profile)
    
    # Check if risk profile already exists
    existing_risk_profile = db.query(RiskProfile).filter(
        RiskProfile.user_id == current_user_id
    ).first()
    
    if existing_risk_profile:
        # Update existing profile and clear cached AI explanation
        existing_risk_profile.risk_score = risk_data['risk_score']
        existing_risk_profile.investor_type = risk_data['investor_type']
        existing_risk_profile.explanation = risk_data['explanation']
        existing_risk_profile.ai_explanation = None  # Clear cached AI - will regenerate on next request
        db.commit()
        db.refresh(existing_risk_profile)
        return existing_risk_profile
    else:
        # Create new risk profile
        new_risk_profile = RiskProfile(
            user_id=current_user_id,
            risk_score=risk_data['risk_score'],
            investor_type=risk_data['investor_type'],
            explanation=risk_data['explanation']
        )
        db.add(new_risk_profile)
        db.commit()
        db.refresh(new_risk_profile)
        return new_risk_profile


@router.get("/", response_model=RiskProfileResponse)
async def get_risk_profile(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get risk profile for authenticated user
    
    Returns the calculated risk profile including:
    - Risk score (0-100)
    - Investor type (Conservative/Moderate/Aggressive)
    - Detailed explanation
    """
    risk_profile = db.query(RiskProfile).filter(
        RiskProfile.user_id == current_user_id
    ).first()
    
    if not risk_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk profile not found. Please calculate your risk profile first."
        )
    
    return risk_profile


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk_profile(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete risk profile for authenticated user
    """
    risk_profile = db.query(RiskProfile).filter(
        RiskProfile.user_id == current_user_id
    ).first()
    
    if not risk_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk profile not found"
        )
    
    db.delete(risk_profile)
    db.commit()
    
    return None


@router.get("/explain")
async def explain_risk_profile(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered explanation of risk profile (cached)
    
    Returns cached AI explanation if available, otherwise generates new one.
    The explanation is saved to database for future requests.
    """
    # Get risk profile
    risk_profile = db.query(RiskProfile).filter(
        RiskProfile.user_id == current_user_id
    ).first()
    
    if not risk_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk profile not found. Please calculate your risk profile first."
        )
    
    # Check if AI explanation is already cached
    if risk_profile.ai_explanation:
        return {
            "risk_score": risk_profile.risk_score,
            "investor_type": risk_profile.investor_type,
            "ai_explanation": risk_profile.ai_explanation,
            "ai_available": True,
            "cached": True
        }
    
    # Generate new AI explanation if not cached
    financial_profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    if not financial_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found"
        )
    
    prompt = OllamaPrompts.risk_classification_explanation(
        risk_score=risk_profile.risk_score,
        investor_type=risk_profile.investor_type,
        age=financial_profile.age,
        income=financial_profile.monthly_income,
        savings_rate=(financial_profile.monthly_savings / financial_profile.monthly_income * 100) if financial_profile.monthly_income > 0 else 0,
        horizon=financial_profile.investment_horizon,
        tolerance=financial_profile.risk_tolerance
    )
    
    result = await ollama_service.generate_explanation(
        prompt=prompt,
        system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
        temperature=0.7
    )
    
    # Cache the AI explanation in database
    if result.get("success", False) and result.get("explanation"):
        risk_profile.ai_explanation = result["explanation"]
        db.commit()
        db.refresh(risk_profile)
    
    return {
        "risk_score": risk_profile.risk_score,
        "investor_type": risk_profile.investor_type,
        "ai_explanation": result.get("explanation", "AI explanation unavailable"),
        "ai_available": result.get("success", False),
        "cached": False
    }
