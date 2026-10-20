"""
Portfolio Analysis API Routes
Handles portfolio risk analysis and metrics calculation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.portfolio_analysis import PortfolioAnalysis
from app.schemas.portfolio_analysis import (
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse,
    PortfolioAnalysisDB,
    RiskInterpretation,
    GenerateSampleDataRequest
)
from app.services.portfolio_risk_analyzer import PortfolioRiskAnalyzer
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts


router = APIRouter()


@router.post("/analyze", response_model=PortfolioAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Analyze portfolio risk metrics for the authenticated user."""
    try:
        portfolio_data = [point.model_dump() for point in request.portfolio_data]
        analysis_result = PortfolioRiskAnalyzer.calculate_portfolio_risk(
            portfolio_data=portfolio_data,
            risk_free_rate=request.risk_free_rate
        )
        interpretation = PortfolioRiskAnalyzer.get_risk_interpretation(analysis_result['risk_level'])
        
        # Save to database with test user
        db_analysis = PortfolioAnalysis(
            user_id=current_user_id,
            volatility=analysis_result['volatility'],
            volatility_percent=analysis_result['volatility_percent'],
            sharpe_ratio=analysis_result['sharpe_ratio'],
            max_drawdown=analysis_result['max_drawdown'],
            max_drawdown_percent=analysis_result['max_drawdown_percent'],
            risk_score=analysis_result['risk_score'],
            risk_level=analysis_result['risk_level'],
            average_return=analysis_result['average_return'],
            average_return_percent=analysis_result['average_return_percent'],
            total_return=analysis_result['total_return'],
            risk_free_rate=analysis_result['risk_free_rate'],
            data_points=analysis_result['data_points'],
            analysis_period_days=analysis_result['analysis_period_days'],
            portfolio_data=portfolio_data,
            ai_explanation=None  # reset cache so /explain generates a fresh AI response
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return PortfolioAnalysisResponse(**analysis_result, interpretation=RiskInterpretation(**interpretation))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=PortfolioAnalysisResponse)
async def get_latest_analysis(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get the authenticated user's latest portfolio analysis."""
    analysis = db.query(PortfolioAnalysis).filter(
        PortfolioAnalysis.user_id == current_user_id
    ).order_by(PortfolioAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    interpretation = PortfolioRiskAnalyzer.get_risk_interpretation(analysis.risk_level)
    return PortfolioAnalysisResponse(
        volatility=analysis.volatility,
        volatility_percent=analysis.volatility_percent,
        sharpe_ratio=analysis.sharpe_ratio,
        max_drawdown=analysis.max_drawdown,
        max_drawdown_percent=analysis.max_drawdown_percent,
        risk_score=analysis.risk_score,
        risk_level=analysis.risk_level,
        average_return=analysis.average_return,
        average_return_percent=analysis.average_return_percent,
        total_return=analysis.total_return,
        risk_free_rate=analysis.risk_free_rate,
        data_points=analysis.data_points,
        analysis_period_days=analysis.analysis_period_days,
        interpretation=RiskInterpretation(**interpretation),
        ai_explanation=analysis.ai_explanation  # ← include cached AI explanation
    )


@router.post("/generate-sample-data")
async def generate_sample_data(
    request: GenerateSampleDataRequest,
    current_user_id: int = Depends(get_current_user),
):
    """Generate sample portfolio data (authenticated: it is a user tool, not a public one)"""
    sample_data = PortfolioRiskAnalyzer.generate_sample_portfolio_data(
        initial_value=request.initial_value,
        days=request.days,
        volatility=request.volatility,
        drift=request.drift
    )
    return {"portfolio_data": sample_data}


@router.get("/explain")
async def explain_portfolio_analysis(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get AI-powered explanation of portfolio risk analysis (cached)

    Returns cached AI explanation if available, otherwise generates new one.
    """
    # Get latest analysis
    analysis = db.query(PortfolioAnalysis).filter(
        PortfolioAnalysis.user_id == current_user_id
    ).order_by(PortfolioAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No portfolio analysis found. Please analyze your portfolio first."
        )
    
    # Check if AI explanation is already cached
    if analysis.ai_explanation:
        return {
            "risk_score": analysis.risk_score,
            "risk_level": analysis.risk_level,
            "volatility_percent": analysis.volatility_percent,
            "sharpe_ratio": analysis.sharpe_ratio,
            "max_drawdown_percent": analysis.max_drawdown_percent,
            "ai_explanation": analysis.ai_explanation,
            "ai_available": True,
            "cached": True
        }
    
    # Generate new AI explanation if not cached
    prompt = f"""Portfolio metrics: Risk Score {analysis.risk_score:.1f}/100 ({analysis.risk_level}), Volatility {analysis.volatility_percent:.1f}%, Sharpe Ratio {analysis.sharpe_ratio:.2f}, Max Drawdown {analysis.max_drawdown_percent:.1f}%, Avg Annual Return {analysis.average_return_percent:.1f}%.

In 3 short points explain: (1) what these numbers mean, (2) is this risk level appropriate, (3) one key action to improve returns. Be concise and practical."""

    result = await ollama_service.generate_explanation(
        prompt=prompt,
        system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
        temperature=0.7,
        max_tokens=400
    )
    
    # Cache the AI explanation in database
    if result.get("success", False) and result.get("explanation"):
        analysis.ai_explanation = result["explanation"]
        db.commit()
        db.refresh(analysis)
    
    return {
        "risk_score": analysis.risk_score,
        "risk_level": analysis.risk_level,
        "volatility_percent": analysis.volatility_percent,
        "sharpe_ratio": analysis.sharpe_ratio,
        "max_drawdown_percent": analysis.max_drawdown_percent,
        "ai_explanation": result.get("explanation", "AI explanation unavailable"),
        "ai_available": result.get("success", False),
        "cached": False
    }
