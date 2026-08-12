"""
Portfolio Analysis API Routes
Handles portfolio risk analysis and metrics calculation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
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

# Hardcode user_id for testing (remove auth requirement)
TEST_USER_ID = 1


@router.post("/analyze", response_model=PortfolioAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze portfolio risk metrics - NO AUTH REQUIRED FOR TESTING"""
    try:
        portfolio_data = [point.model_dump() for point in request.portfolio_data]
        analysis_result = PortfolioRiskAnalyzer.calculate_portfolio_risk(
            portfolio_data=portfolio_data,
            risk_free_rate=request.risk_free_rate
        )
        interpretation = PortfolioRiskAnalyzer.get_risk_interpretation(analysis_result['risk_level'])
        
        # Save to database with test user
        db_analysis = PortfolioAnalysis(
            user_id=TEST_USER_ID,
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
            portfolio_data=portfolio_data
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return PortfolioAnalysisResponse(**analysis_result, interpretation=RiskInterpretation(**interpretation))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=PortfolioAnalysisResponse)
async def get_latest_analysis(db: Session = Depends(get_db)):
    """Get latest portfolio analysis - NO AUTH REQUIRED"""
    analysis = db.query(PortfolioAnalysis).filter(
        PortfolioAnalysis.user_id == TEST_USER_ID
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
        interpretation=RiskInterpretation(**interpretation)
    )


@router.post("/generate-sample-data")
async def generate_sample_data(request: GenerateSampleDataRequest):
    """Generate sample portfolio data"""
    sample_data = PortfolioRiskAnalyzer.generate_sample_portfolio_data(
        initial_value=request.initial_value,
        days=request.days,
        volatility=request.volatility,
        drift=request.drift
    )
    return {"portfolio_data": sample_data}


@router.get("/explain")
async def explain_portfolio_analysis(db: Session = Depends(get_db)):
    """
    Get AI-powered explanation of portfolio risk analysis (cached)
    
    Returns cached AI explanation if available, otherwise generates new one.
    """
    # Get latest analysis
    analysis = db.query(PortfolioAnalysis).filter(
        PortfolioAnalysis.user_id == TEST_USER_ID
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
    prompt = f"""Analyze this portfolio risk profile and provide actionable insights:

**Portfolio Risk Metrics:**
- Risk Score: {analysis.risk_score:.1f}/100
- Risk Level: {analysis.risk_level}
- Volatility (Annualized): {analysis.volatility_percent:.2f}%
- Sharpe Ratio: {analysis.sharpe_ratio:.2f}
- Maximum Drawdown: {analysis.max_drawdown_percent:.2f}%
- Average Annual Return: {analysis.average_return_percent:.2f}%
- Total Return: {analysis.total_return:.2f}%

**Analysis Period:** {analysis.analysis_period_days} days with {analysis.data_points} data points

Please provide:
1. What these metrics reveal about portfolio risk and performance
2. Is this risk level appropriate for different investor types?
3. Specific recommendations to improve risk-adjusted returns
4. Red flags or concerns based on these numbers
5. Action items for portfolio optimization

Keep it practical, data-driven, and actionable. Use markdown formatting."""

    result = await ollama_service.generate_explanation(
        prompt=prompt,
        system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
        temperature=0.7
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
