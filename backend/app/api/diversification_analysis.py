"""
Diversification Analysis API Routes
Handles portfolio diversification analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.diversification_analysis import DiversificationAnalysis
from app.schemas.diversification_analysis import (
    DiversificationAnalysisRequest,
    DiversificationAnalysisResponse,
    DiversificationAnalysisDB,
    SectorConcentration,
    AssetConcentration,
    GenerateSampleHoldingsRequest
)
from app.services.diversification_analyzer import DiversificationAnalyzer
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts


router = APIRouter()


@router.post("/analyze", response_model=DiversificationAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_diversification(
    request: DiversificationAnalysisRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Analyze portfolio diversification for the authenticated user."""
    try:
        # Convert holdings to dict format
        holdings = [holding.model_dump() for holding in request.holdings]
        
        # Perform diversification analysis
        analysis_result = DiversificationAnalyzer.calculate_diversification_score(holdings)
        
        # Save to database with test user
        db_analysis = DiversificationAnalysis(
            user_id=current_user_id,
            diversification_score=analysis_result['diversification_score'],
            hhi_score=analysis_result['hhi_score'],
            num_holdings=analysis_result['num_holdings'],
            total_value=analysis_result['total_value'],
            sector_concentration=analysis_result['sector_concentration'],
            asset_concentration=analysis_result['asset_concentration'],
            warnings=analysis_result['warnings'],
            recommendations=analysis_result['recommendations'],
            holdings_data=holdings
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        # Return response
        return DiversificationAnalysisResponse(
            diversification_score=analysis_result['diversification_score'],
            hhi_score=analysis_result['hhi_score'],
            num_holdings=analysis_result['num_holdings'],
            total_value=analysis_result['total_value'],
            sector_concentration=SectorConcentration(**analysis_result['sector_concentration']),
            asset_concentration=AssetConcentration(**analysis_result['asset_concentration']),
            warnings=analysis_result['warnings'],
            recommendations=analysis_result['recommendations']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=DiversificationAnalysisResponse)
async def get_latest_analysis(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get the authenticated user's latest diversification analysis."""
    analysis = db.query(DiversificationAnalysis).filter(
        DiversificationAnalysis.user_id == current_user_id
    ).order_by(DiversificationAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No diversification analysis found")
    
    return DiversificationAnalysisResponse(
        diversification_score=analysis.diversification_score,
        hhi_score=analysis.hhi_score,
        num_holdings=analysis.num_holdings,
        total_value=analysis.total_value,
        sector_concentration=SectorConcentration(**analysis.sector_concentration),
        asset_concentration=AssetConcentration(**analysis.asset_concentration),
        warnings=analysis.warnings or [],
        recommendations=analysis.recommendations or []
    )


@router.get("/history", response_model=List[DiversificationAnalysisDB])
async def get_analysis_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get the authenticated user's diversification analysis history."""
    analyses = db.query(DiversificationAnalysis).filter(
        DiversificationAnalysis.user_id == current_user_id
    ).order_by(DiversificationAnalysis.created_at.desc()).limit(limit).all()
    
    return analyses


@router.post("/generate-sample-holdings")
async def generate_sample_holdings(request: GenerateSampleHoldingsRequest):
    """Generate sample holdings for testing"""
    holdings = DiversificationAnalyzer.generate_sample_holdings(
        portfolio_value=request.portfolio_value,
        diversified=request.diversified
    )
    return {"holdings": holdings}


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete one of the authenticated user's diversification analyses."""
    analysis = db.query(DiversificationAnalysis).filter(
        DiversificationAnalysis.id == analysis_id,
        DiversificationAnalysis.user_id == current_user_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    
    return None


@router.get("/explain")
async def explain_diversification_analysis(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get AI-powered explanation of diversification analysis (cached)

    Returns cached AI explanation if available, otherwise generates new one.
    """
    # Get latest analysis
    analysis = db.query(DiversificationAnalysis).filter(
        DiversificationAnalysis.user_id == current_user_id
    ).order_by(DiversificationAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No diversification analysis found. Please analyze your portfolio first."
        )
    
    # Check if AI explanation is already cached
    if analysis.ai_explanation:
        return {
            "diversification_score": analysis.diversification_score,
            "hhi_score": analysis.hhi_score,
            "num_holdings": analysis.num_holdings,
            "ai_explanation": analysis.ai_explanation,
            "ai_available": True,
            "cached": True
        }
    
    # Generate new AI explanation if not cached
    sector_data = "\n".join([f"  - {k}: {v:.1f}%" for k, v in analysis.sector_concentration.get('sectors', {}).items()])
    asset_data = "\n".join([f"  - {k}: {v:.1f}%" for k, v in analysis.asset_concentration.get('assets', {}).items()])
    warnings_text = "\n".join([f"  • {w}" for w in (analysis.warnings or [])])
    
    prompt = f"""Analyze this portfolio diversification and provide actionable insights:

**Diversification Metrics:**
- Diversification Score: {analysis.diversification_score:.1f}/100
- HHI (Herfindahl-Hirschman Index): {analysis.hhi_score:.2f}
- Number of Holdings: {analysis.num_holdings}
- Total Portfolio Value: ₹{analysis.total_value:,.0f}

**Sector Concentration:**
{sector_data}
- Top Sector: {analysis.sector_concentration.get('top_sector', 'N/A')} ({analysis.sector_concentration.get('top_sector_percentage', 0):.1f}%)
- Number of Sectors: {analysis.sector_concentration.get('num_sectors', 0)}

**Asset Type Concentration:**
{asset_data}
- Top Asset: {analysis.asset_concentration.get('top_asset', 'N/A')} ({analysis.asset_concentration.get('top_asset_percentage', 0):.1f}%)
- Number of Asset Types: {analysis.asset_concentration.get('num_asset_types', 0)}

**Current Warnings:**
{warnings_text if warnings_text else "  • No major concentration warnings"}

Please provide:
1. Interpretation of the diversification score and what it means
2. Analysis of concentration risks (sector and asset)
3. Is this level of diversification appropriate?
4. Specific actions to improve diversification
5. Which sectors/assets to add or reduce

Keep it practical and actionable. Use markdown formatting."""

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
        "diversification_score": analysis.diversification_score,
        "hhi_score": analysis.hhi_score,
        "num_holdings": analysis.num_holdings,
        "ai_explanation": result.get("explanation", "AI explanation unavailable"),
        "ai_available": result.get("success", False),
        "cached": False
    }
