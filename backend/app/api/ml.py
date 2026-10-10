"""
ML Prediction API Routes
Volatility forecasting endpoints.

Labelling note: these endpoints serve the ML-BASED VOLATILITY FORECAST.
They are unrelated to the Ollama-generated prose served by the various
`/explain` endpoints. The two are distinct features and are deliberately
kept on separate routers so the distinction survives into the API
surface:

    /api/ml/*       ML-based volatility forecasting (this file)
    /api/*/explain  AI-generated explanation (Ollama / qwen2.5)
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.ml.data import InvalidTickerError, PriceDataError, cache_status
from app.ml.model_registry import list_artifacts
from app.schemas.ml_prediction import (
    CacheStatusResponse,
    FeatureSnapshotResponse,
    ModelInfoResponse,
    TrendOutlookResponse,
    VolatilityForecastResponse,
    VolatilityPredictionRequest,
)
from app.services.ml_prediction_service import volatility_prediction_service
from app.services.stock_trend_service import stock_trend_service


router = APIRouter()


@router.post("/predict-volatility", response_model=VolatilityForecastResponse)
async def predict_volatility(
    request: VolatilityPredictionRequest,
    current_user_id: int = Depends(get_current_user),
):
    """
    Forecast annualised volatility for a ticker.

    Returns a usable figure whenever price history is obtainable. Check
    `source` before describing the result: 'ml_predicted' is a model
    output, 'historical_fallback' is trailing realised volatility and
    must not be presented as a prediction.
    """
    try:
        forecast = volatility_prediction_service.get_forecast(
            ticker=request.ticker,
            use_cache=request.use_cache,
        )
    except PriceDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Price data unavailable for {request.ticker}: {exc}",
        )

    return VolatilityForecastResponse(
        ticker=forecast.ticker,
        volatility=round(forecast.volatility, 6),
        volatility_percent=round(forecast.volatility * 100, 2),
        source=forecast.source,
        horizon_days=forecast.horizon_days,
        predicted_volatility=(
            round(forecast.predicted_volatility, 6)
            if forecast.predicted_volatility is not None else None
        ),
        historical_volatility=(
            round(forecast.historical_volatility, 6)
            if forecast.historical_volatility is not None else None
        ),
        model_version=forecast.model_version,
        fallback_reason=forecast.fallback_reason,
        as_of=forecast.as_of,
    )


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info(current_user_id: int = Depends(get_current_user)):
    """
    Report whether a volatility model is loaded, and its metadata.

    Before training, `model_loaded` is false and `error` explains that no
    artifact exists — that is the expected state, not a malfunction.
    """
    return ModelInfoResponse(**volatility_prediction_service.model_info())


@router.post("/reload-model", response_model=ModelInfoResponse)
async def reload_model(current_user_id: int = Depends(get_current_user)):
    """
    Re-read the model artifact from disk.

    Use after saving a newly trained model, to pick it up without
    restarting the API.

    TODO: gate behind an admin role once the user model has one. Any
    authenticated user can currently trigger a reload.
    """
    result = volatility_prediction_service.reload_model()
    return ModelInfoResponse(
        model_loaded=result["model_loaded"],
        horizon_days=volatility_prediction_service.model_info()["horizon_days"],
        fallback="trailing 21-day realised volatility",
        error=result["error"],
        model=result["model"],
    )


@router.get("/features/{ticker}", response_model=FeatureSnapshotResponse)
async def get_feature_snapshot(
    ticker: str,
    current_user_id: int = Depends(get_current_user),
):
    """
    Show the feature values a prediction for `ticker` would be based on.

    When a forecast looks wrong, this is the first place to look — the
    cause is usually an input, not the estimator.
    """
    try:
        return FeatureSnapshotResponse(
            **volatility_prediction_service.feature_snapshot(ticker)
        )
    except PriceDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Price data unavailable for {ticker}: {exc}",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/trend-outlook/{ticker}", response_model=TrendOutlookResponse)
def get_trend_outlook(
    ticker: str,
    current_user_id: int = Depends(get_current_user),
):
    """
    21-day outlook for a stock: current trend, probability of a rise, and
    the expected price range.

    Check `probability_source` before describing the probability:
    'ml_predicted' is a model output, while 'historical_base_rate' is the
    stock's own past frequency of rising and must not be presented as a
    prediction.

    Plain `def` so FastAPI runs the blocking price fetch in its threadpool.
    """
    try:
        return TrendOutlookResponse(**stock_trend_service.get_outlook(ticker))
    except InvalidTickerError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except PriceDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Price data unavailable for {ticker}: {exc}",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/trend-model-info", response_model=ModelInfoResponse)
def get_trend_model_info(current_user_id: int = Depends(get_current_user)):
    """
    Report whether a trend classifier is loaded, and its held-out metrics.

    Before training, `model_loaded` is false: the expected state, not a fault.
    """
    return ModelInfoResponse(**stock_trend_service.model_info())


@router.post("/reload-trend-model", response_model=ModelInfoResponse)
def reload_trend_model(current_user_id: int = Depends(get_current_user)):
    """
    Re-read the trend artifact from disk after training.

    TODO: gate behind an admin role once the user model has one, as with
    /reload-model.
    """
    result = stock_trend_service.reload_model()
    return ModelInfoResponse(
        model_loaded=result["model_loaded"],
        horizon_days=stock_trend_service.model_info()["horizon_days"],
        fallback=stock_trend_service.model_info()["fallback"],
        error=result["error"],
        model=result["model"],
    )


@router.get("/cache-status", response_model=CacheStatusResponse)
async def get_cache_status(current_user_id: int = Depends(get_current_user)):
    """Inspect the on-disk price cache and the available model artifacts."""
    return CacheStatusResponse(
        cache_entries=cache_status(),
        artifacts=list_artifacts(),
    )
