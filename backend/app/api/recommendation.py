"""
Portfolio Recommendation API Routes
Handles automated portfolio allocation recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_current_user_id
from app.models.portfolio_recommendation import PortfolioRecommendation
from app.models.risk_profile import RiskProfile
from app.models.financial_profile import FinancialProfile
from app.models.user import User
from app.schemas.portfolio_recommendation import PortfolioRecommendationResponse
from app.services.recommendation_engine import RecommendationEngine
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts


router = APIRouter()




@router.post("/generate", response_model=PortfolioRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def generate_recommendation(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate portfolio recommendation based on risk profile
    
    Requires risk profile to exist.
    Generates allocation recommendations:
    - Conservative: Stocks 20%, MF 50%, Gold 20%, Emergency 10%
    - Moderate: Stocks 45%, MF 35%, Gold 10%, Emergency 10%
    - Aggressive: Stocks 70%, MF 20%, Gold 5%, Emergency 5%
    
    Returns detailed allocation with summary
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
    
    # Get financial profile for monthly savings info
    financial_profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    monthly_savings = financial_profile.monthly_savings if financial_profile else None
    
    # Generate recommendation
    recommendation_data = RecommendationEngine.generate_recommendation(
        risk_profile.investor_type,
        risk_profile.risk_score,
        monthly_savings
    )
    
    # Check if recommendation already exists
    existing_recommendation = db.query(PortfolioRecommendation).filter(
        PortfolioRecommendation.user_id == current_user_id
    ).first()
    
    if existing_recommendation:
        # Update existing recommendation and clear cached AI explanation
        existing_recommendation.stocks_percent = recommendation_data['stocks_percent']
        existing_recommendation.mutual_funds_percent = recommendation_data['mutual_funds_percent']
        existing_recommendation.gold_percent = recommendation_data['gold_percent']
        existing_recommendation.emergency_percent = recommendation_data['emergency_percent']
        existing_recommendation.recommendation_summary = recommendation_data['recommendation_summary']
        existing_recommendation.ai_explanation = None  # Clear cached AI - will regenerate on next request
        db.commit()
        db.refresh(existing_recommendation)
        return existing_recommendation
    else:
        # Create new recommendation
        new_recommendation = PortfolioRecommendation(
            user_id=current_user_id,
            stocks_percent=recommendation_data['stocks_percent'],
            mutual_funds_percent=recommendation_data['mutual_funds_percent'],
            gold_percent=recommendation_data['gold_percent'],
            emergency_percent=recommendation_data['emergency_percent'],
            recommendation_summary=recommendation_data['recommendation_summary']
        )
        db.add(new_recommendation)
        db.commit()
        db.refresh(new_recommendation)
        return new_recommendation


@router.get("/", response_model=PortfolioRecommendationResponse)
async def get_recommendation(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio recommendation for authenticated user
    
    Returns the generated recommendation including:
    - Allocation percentages for each asset class
    - Detailed summary with investment guidance
    """
    recommendation = db.query(PortfolioRecommendation).filter(
        PortfolioRecommendation.user_id == current_user_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio recommendation not found. Please generate your recommendation first."
        )
    
    return recommendation


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete portfolio recommendation for authenticated user
    """
    recommendation = db.query(PortfolioRecommendation).filter(
        PortfolioRecommendation.user_id == current_user_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio recommendation not found"
        )
    
    db.delete(recommendation)
    db.commit()
    
    return None


@router.get("/explain")
async def explain_recommendation(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered explanation of portfolio recommendation (cached)
    
    Returns cached AI explanation if available, otherwise generates new one.
    """
    # Get recommendation
    recommendation = db.query(PortfolioRecommendation).filter(
        PortfolioRecommendation.user_id == current_user_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio recommendation not found. Please generate your recommendation first."
        )
    
    # Check if AI explanation is already cached
    if recommendation.ai_explanation:
        return {
            "stocks_percent": recommendation.stocks_percent,
            "mutual_funds_percent": recommendation.mutual_funds_percent,
            "gold_percent": recommendation.gold_percent,
            "emergency_percent": recommendation.emergency_percent,
            "ai_explanation": recommendation.ai_explanation,
            "ai_available": True,
            "cached": True
        }
    
    # Generate new AI explanation if not cached
    risk_profile = db.query(RiskProfile).filter(
        RiskProfile.user_id == current_user_id
    ).first()
    
    financial_profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user_id
    ).first()
    
    prompt = OllamaPrompts.portfolio_recommendation_explanation(
        investor_type=risk_profile.investor_type if risk_profile else "Moderate",
        risk_score=risk_profile.risk_score if risk_profile else 50.0,
        stocks_percent=recommendation.stocks_percent,
        mutual_funds_percent=recommendation.mutual_funds_percent,
        gold_percent=recommendation.gold_percent,
        emergency_percent=recommendation.emergency_percent,
        monthly_savings=financial_profile.monthly_savings if financial_profile else None
    )
    
    result = await ollama_service.generate_explanation(
        prompt=prompt,
        system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
        temperature=0.7,
        max_tokens=400
    )
    
    # Cache the AI explanation in database
    if result.get("success", False) and result.get("explanation"):
        recommendation.ai_explanation = result["explanation"]
        db.commit()
        db.refresh(recommendation)
    
    return {
        "stocks_percent": recommendation.stocks_percent,
        "mutual_funds_percent": recommendation.mutual_funds_percent,
        "gold_percent": recommendation.gold_percent,
        "emergency_percent": recommendation.emergency_percent,
        "ai_explanation": result.get("explanation", "AI explanation unavailable"),
        "ai_available": result.get("success", False),
        "cached": False
    }
