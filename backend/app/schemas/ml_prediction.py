"""
ML Prediction Schemas
Pydantic models for the volatility forecasting endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional


class VolatilityPredictionRequest(BaseModel):
    """Request a volatility forecast for one ticker."""
    ticker: str = Field(
        ..., min_length=1, max_length=32,
        description="Yahoo Finance symbol, e.g. 'RELIANCE.NS'"
    )
    use_cache: bool = Field(
        default=True,
        description="Serve a recent in-process forecast if one exists"
    )

    @field_validator("ticker")
    @classmethod
    def normalise_ticker(cls, v: str) -> str:
        return v.strip().upper()

    class Config:
        json_schema_extra = {"example": {"ticker": "RELIANCE.NS"}}


class VolatilityForecastResponse(BaseModel):
    """
    A volatility forecast and its provenance.

    `source` distinguishes a genuine model prediction from the fallback,
    so the caller can label it correctly instead of presenting trailing
    realised volatility as "ML-based".
    """
    ticker: str
    volatility: float = Field(..., description="Annualised volatility to use (decimal)")
    volatility_percent: float = Field(..., description="Same value as a percentage")
    source: str = Field(..., description="'ml_predicted' | 'historical_fallback'")
    horizon_days: int = Field(..., description="Forecast horizon in trading days")

    predicted_volatility: Optional[float] = Field(
        None, description="Raw model output, when a model produced one"
    )
    historical_volatility: Optional[float] = Field(
        None, description="Trailing realised volatility, for comparison"
    )
    model_version: Optional[str] = Field(None, description="Artifact identifier")
    fallback_reason: Optional[str] = Field(
        None, description="Why the model output was not used, when applicable"
    )
    as_of: Optional[str] = Field(None, description="Date of the feature row used")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "RELIANCE.NS",
                "volatility": 0.2431,
                "volatility_percent": 24.31,
                "source": "ml_predicted",
                "horizon_days": 21,
                "predicted_volatility": 0.2431,
                "historical_volatility": 0.2210,
                "model_version": "ridge-har-v1",
                "as_of": "2026-10-02"
            }
        }


class ModelInfoResponse(BaseModel):
    """State of the volatility model currently loaded by the API."""
    model_loaded: bool
    horizon_days: int
    fallback: str = Field(..., description="What is used when no model is available")
    error: Optional[str] = Field(None, description="Why loading failed, if it did")
    model: Optional[Dict[str, Any]] = Field(
        None, description="Artifact metadata: version, estimator, metrics, features"
    )

    # `model_*` would otherwise collide with Pydantic's protected namespace
    model_config = {"protected_namespaces": ()}


class FeatureSnapshotResponse(BaseModel):
    """Current feature values for a ticker, for debugging predictions."""
    ticker: str
    as_of: str
    rows_available: int
    complete_rows: int
    features: Dict[str, Optional[float]]


class CacheStatusResponse(BaseModel):
    """Contents of the on-disk price cache."""
    cache_entries: List[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
