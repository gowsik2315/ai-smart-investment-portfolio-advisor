"""
Diversification Analysis Schemas
Pydantic models for diversification analysis
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class HoldingInput(BaseModel):
    """Portfolio holding input"""
    name: str = Field(..., description="Name of the holding")
    value: float = Field(..., gt=0, description="Value of the holding")
    sector: str = Field(..., description="Sector (e.g., Technology, Banking)")
    asset_type: str = Field(..., description="Asset type (e.g., Stocks, Bonds, Mutual Funds)")


class DiversificationAnalysisRequest(BaseModel):
    """Request model for diversification analysis"""
    holdings: List[HoldingInput] = Field(
        ..., 
        min_items=1,
        description="List of portfolio holdings"
    )


class SectorConcentration(BaseModel):
    """Sector concentration details"""
    sectors: Dict[str, float] = Field(..., description="Sector-wise percentages")
    top_sector: str = Field(..., description="Sector with highest concentration")
    top_sector_percentage: float = Field(..., description="Top sector percentage")
    num_sectors: int = Field(..., description="Number of sectors")


class AssetConcentration(BaseModel):
    """Asset concentration details"""
    assets: Dict[str, float] = Field(..., description="Asset type percentages")
    top_asset: str = Field(..., description="Asset type with highest concentration")
    top_asset_percentage: float = Field(..., description="Top asset percentage")
    num_asset_types: int = Field(..., description="Number of asset types")


class DiversificationAnalysisResponse(BaseModel):
    """Response model with analysis results"""
    diversification_score: float = Field(..., ge=0, le=100, description="Diversification score (0-100)")
    sector_concentration: SectorConcentration
    asset_concentration: AssetConcentration
    hhi_score: float = Field(..., description="Herfindahl-Hirschman Index")
    num_holdings: int = Field(..., description="Number of holdings")
    total_value: float = Field(..., description="Total portfolio value")
    warnings: List[str] = Field(..., description="Warning messages")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    ai_explanation: Optional[str] = Field(None, description="AI-generated explanation (cached)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "diversification_score": 75.5,
                "sector_concentration": {
                    "sectors": {"Technology": 30.0, "Banking": 25.0, "Energy": 20.0},
                    "top_sector": "Technology",
                    "top_sector_percentage": 30.0,
                    "num_sectors": 3
                },
                "asset_concentration": {
                    "assets": {"Stocks": 60.0, "Bonds": 30.0, "Gold": 10.0},
                    "top_asset": "Stocks",
                    "top_asset_percentage": 60.0,
                    "num_asset_types": 3
                },
                "hhi_score": 25.5,
                "num_holdings": 10,
                "total_value": 1000000.0,
                "warnings": ["✅ No major concentration risks detected"],
                "recommendations": ["✅ Excellent diversification!"]
            }
        }


class DiversificationAnalysisDB(BaseModel):
    """Database model response"""
    id: int
    user_id: int
    diversification_score: float
    hhi_score: float
    num_holdings: int
    total_value: float
    sector_concentration: Dict
    asset_concentration: Dict
    warnings: Optional[List[str]]
    recommendations: Optional[List[str]]
    ai_explanation: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GenerateSampleHoldingsRequest(BaseModel):
    """Request model for generating sample holdings"""
    portfolio_value: float = Field(default=1000000, gt=0, description="Total portfolio value")
    diversified: bool = Field(default=True, description="True for diversified, False for concentrated")
