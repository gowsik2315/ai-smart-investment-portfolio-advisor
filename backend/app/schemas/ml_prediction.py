"""
ML Prediction Schemas
Pydantic models for the volatility forecasting endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional

from app.ml.data import InvalidTickerError, validate_ticker


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
        try:
            return validate_ticker(v)
        except InvalidTickerError as exc:
            raise ValueError(str(exc)) from exc

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


# ── Stock trend outlook ──────────────────────────────────────────────

class TrendSignal(BaseModel):
    """One technical signal contributing to the descriptive trend."""
    name: str
    label: str
    value: float = Field(..., description="Signal magnitude (a ratio or log return)")
    bullish: bool
    detail: str


class TrendSummary(BaseModel):
    """Where the stock is trending now. A description of the past, not a forecast."""
    label: str = Field(..., description="Bullish | Neutral | Bearish")
    score: float = Field(..., description="-1 (all signals bearish) to +1 (all bullish)")
    signals: List[TrendSignal]
    rsi_14: Optional[float] = None
    rsi_state: Optional[str] = Field(None, description="overbought | neutral | oversold")


class RangePoint(BaseModel):
    """Expected price bounds `day` trading days after the last close."""
    day: int
    median: float
    lower_68: float
    upper_68: float
    lower_95: float
    upper_95: float


class PricePoint(BaseModel):
    date: str
    close: float


class TrendOutlookResponse(BaseModel):
    """
    The 21-day outlook for one stock.

    Check `probability_source` before describing `probability_up`:
    'ml_predicted' is a model output; 'historical_base_rate' is the stock's
    own past frequency of rising and is NOT a prediction.
    """
    ticker: str
    as_of: str = Field(..., description="Date of the last close used")
    last_close: float
    horizon_days: int

    probability_up: float = Field(..., description="Chance of closing higher at the horizon")
    probability_source: str = Field(..., description="'ml_predicted' | 'historical_base_rate'")
    base_rate_up: float = Field(
        ..., description="Historical share of 21-day windows that ended higher; the bar a model must beat"
    )
    model_version: Optional[str] = None
    fallback_reason: Optional[str] = None
    model_metrics: Optional[Dict[str, Optional[float]]] = Field(
        None, description="Held-out scores stored in the artifact, when a model is loaded"
    )

    trend: TrendSummary

    volatility: float = Field(..., description="Annualised volatility used for the range (decimal)")
    volatility_source: str = Field(..., description="'ml_predicted' | 'historical_fallback'")
    volatility_fallback_reason: Optional[str] = None
    expected_range: List[RangePoint] = Field(
        ..., description="Day-by-day bands centred on the last close; carries no directional view"
    )

    recent_prices: List[PricePoint]
    disclaimer: str

    model_config = {"protected_namespaces": ()}


class TrendExplanationResponse(BaseModel):
    """
    AI-generated (Ollama) explanation of a trend outlook.

    This is generated prose, not a model output. `ai_available` is false
    when Ollama is disabled or fails; `ai_explanation` then holds a short
    notice rather than an explanation.
    """
    ticker: str
    as_of: str
    probability_source: str = Field(..., description="Which source the explained probability had")
    ai_explanation: str
    ai_available: bool
    cached: bool = Field(False, description="Served from the in-memory cache, not freshly generated")
    disclaimer: str
