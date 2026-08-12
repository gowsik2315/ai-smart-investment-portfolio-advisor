"""
SIP Plan API Routes
Handles SIP calculator and plan management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.sip_plan import SIPPlan
from app.models.user import User
from app.schemas.sip_plan import (
    SIPCalculationRequest,
    SIPCalculationResponse,
    SIPPlanCreate,
    SIPPlanUpdate,
    SIPPlanResponse
)
from app.services.sip_calculator import SIPCalculator
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


@router.post("/calculate", response_model=SIPCalculationResponse)
async def calculate_sip(
    calculation: SIPCalculationRequest,
    current_user_id: int = Depends(get_current_user)
):
    """
    Calculate SIP returns
    
    Provides:
    - Total invested amount
    - Wealth generated (returns)
    - Future value
    - Year-wise breakdown
    
    Formula: FV = P × ({[1 + r]^n - 1} / r) × (1 + r)
    """
    try:
        result = SIPCalculator.calculate_sip(
            monthly_investment=calculation.monthly_investment,
            annual_return_rate=calculation.annual_return_rate,
            investment_duration_years=calculation.investment_duration_years
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/explain")
async def explain_sip_calculation(
    calculation: SIPCalculationRequest,
    current_user_id: int = Depends(get_current_user)
):
    """
    Get AI-powered explanation of SIP calculation
    
    Returns detailed AI-generated explanation of:
    - How SIP helps in wealth creation
    - Power of compounding
    - Why SIP is better than lump-sum
    - Tips for staying disciplined
    
    Note: This endpoint ONLY generates AI explanation.
    Use /calculate endpoint first to get calculation results instantly.
    """
    try:
        # Calculate SIP to get values for AI prompt
        result = SIPCalculator.calculate_sip(
            monthly_investment=calculation.monthly_investment,
            annual_return_rate=calculation.annual_return_rate,
            investment_duration_years=calculation.investment_duration_years
        )
        
        # Generate AI explanation prompt
        prompt = OllamaPrompts.sip_explanation(
            monthly_investment=calculation.monthly_investment,
            duration_years=calculation.investment_duration_years,
            annual_return=calculation.annual_return_rate,
            total_invested=result['total_invested'],
            future_value=result['future_value'],
            wealth_generated=result['wealth_generated']
        )
        
        # Get AI explanation
        ai_result = await ollama_service.generate_explanation(
            prompt=prompt,
            system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
            temperature=0.7
        )
        
        return {
            "ai_explanation": ai_result.get("explanation", "AI explanation unavailable"),
            "cached": False  # SIP explanations are always fresh (not cached in DB)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/plans", response_model=SIPPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_sip_plan(
    plan_data: SIPPlanCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new SIP plan
    
    Saves SIP plan with projections to database
    """
    # Calculate projections
    years = plan_data.duration_months / 12
    calculation = SIPCalculator.calculate_sip(
        monthly_investment=plan_data.investment_amount,
        annual_return_rate=plan_data.expected_return_rate,
        investment_duration_years=int(years) if years == int(years) else years
    )
    
    # Calculate end date
    end_date = plan_data.start_date + timedelta(days=plan_data.duration_months * 30)
    
    # Create new SIP plan
    new_plan = SIPPlan(
        user_id=current_user_id,
        plan_name=plan_data.plan_name,
        investment_amount=plan_data.investment_amount,
        frequency=plan_data.frequency,
        start_date=plan_data.start_date,
        end_date=end_date,
        duration_months=plan_data.duration_months,
        equity_percentage=plan_data.equity_percentage,
        debt_percentage=plan_data.debt_percentage,
        gold_percentage=plan_data.gold_percentage,
        expected_return_rate=plan_data.expected_return_rate,
        projected_corpus=calculation['future_value'],
        total_investment=calculation['total_invested'],
        status="Active",
        is_active=True
    )
    
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return new_plan


@router.get("/plans", response_model=List[SIPPlanResponse])
async def get_sip_plans(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None
):
    """
    Get all SIP plans for authenticated user
    
    Optional filter by status: Active, Completed, Paused, Cancelled
    """
    query = db.query(SIPPlan).filter(SIPPlan.user_id == current_user_id)
    
    if status_filter:
        query = query.filter(SIPPlan.status == status_filter)
    
    plans = query.order_by(SIPPlan.created_at.desc()).all()
    return plans


@router.get("/plans/{plan_id}", response_model=SIPPlanResponse)
async def get_sip_plan(
    plan_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific SIP plan by ID
    """
    plan = db.query(SIPPlan).filter(
        SIPPlan.id == plan_id,
        SIPPlan.user_id == current_user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SIP plan not found"
        )
    
    return plan


@router.put("/plans/{plan_id}", response_model=SIPPlanResponse)
async def update_sip_plan(
    plan_id: int,
    plan_update: SIPPlanUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update SIP plan
    """
    plan = db.query(SIPPlan).filter(
        SIPPlan.id == plan_id,
        SIPPlan.user_id == current_user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SIP plan not found"
        )
    
    # Update fields
    update_data = plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    # Recalculate projections if investment amount or return rate changed
    if 'investment_amount' in update_data or 'expected_return_rate' in update_data:
        years = plan.duration_months / 12
        calculation = SIPCalculator.calculate_sip(
            monthly_investment=plan.investment_amount,
            annual_return_rate=plan.expected_return_rate,
            investment_duration_years=int(years) if years == int(years) else years
        )
        plan.projected_corpus = calculation['future_value']
        plan.total_investment = calculation['total_invested']
    
    db.commit()
    db.refresh(plan)
    
    return plan


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sip_plan(
    plan_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete SIP plan
    """
    plan = db.query(SIPPlan).filter(
        SIPPlan.id == plan_id,
        SIPPlan.user_id == current_user_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SIP plan not found"
        )
    
    db.delete(plan)
    db.commit()
    
    return None
