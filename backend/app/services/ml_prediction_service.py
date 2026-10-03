"""
Volatility Prediction Service

The seam between the trained volatility model and the rest of the app.

Design rule: this service NEVER leaves a caller without a usable sigma
just because the ML side is unavailable. Monte Carlo is a user-facing
feature and must keep working whether or not a model artifact exists,
whether or not Yahoo responds, and whether or not the model returns
something sane. Every degradation is recorded in `source` and
`fallback_reason` so the response can say honestly where the number came
from, rather than passing a fallback off as a prediction.

Fallback chain:
    1. ML forecast from the saved artifact
    2. Trailing 21-day realised volatility from the same price history
    3. Raise — only when no price history can be obtained at all
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

import numpy as np

from app.ml.config import (
    HORIZON_DAYS,
    INFERENCE_LOOKBACK_DAYS,
    INDEX_TICKER,
    MAX_PLAUSIBLE_VOLATILITY,
    MIN_PLAUSIBLE_VOLATILITY,
    TRADING_DAYS_PER_YEAR,
)
from app.ml.data import PriceDataError, load_history
from app.ml.features import build_features, latest_feature_row
from app.ml.model_registry import (
    ModelContractError,
    VolatilityModelArtifact,
    load_model,
)

logger = logging.getLogger(__name__)

# Volatility source labels, mirrored in the DB column and API responses
SOURCE_ML = "ml_predicted"
SOURCE_HISTORICAL = "historical_fallback"
SOURCE_MANUAL = "manual"

# Forecasts are cached briefly in-process. Daily bars do not move
# intraday, so repeated simulations in one session need not refetch.
FORECAST_CACHE_TTL_SECONDS = 15 * 60

# yfinance period string covering INFERENCE_LOOKBACK_DAYS trading days
# with slack for weekends and holidays.
_INFERENCE_PERIOD = "3y"


@dataclass
class VolatilityForecast:
    """A volatility figure plus an honest account of where it came from."""

    ticker: str
    volatility: float                      # the value to actually use
    source: str                            # SOURCE_ML | SOURCE_HISTORICAL
    horizon_days: int = HORIZON_DAYS
    predicted_volatility: Optional[float] = None   # model output, if any
    historical_volatility: Optional[float] = None  # trailing realised, always set
    model_version: Optional[str] = None
    fallback_reason: Optional[str] = None
    as_of: Optional[str] = None            # date of the feature row used

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VolatilityPredictionService:
    """
    Loads the volatility model once and serves forecasts.

    Thread-safe: FastAPI runs request handlers concurrently, and model
    loading must not race.
    """

    def __init__(self) -> None:
        self._artifact: Optional[VolatilityModelArtifact] = None
        self._load_attempted = False
        self._load_error: Optional[str] = None
        self._lock = threading.Lock()
        self._cache: Dict[str, tuple[float, VolatilityForecast]] = {}

    # ── Model lifecycle ─────────────────────────────────────────────

    def _ensure_model(self) -> Optional[VolatilityModelArtifact]:
        """
        Load the artifact on first use.

        A missing artifact is the expected state before training, so it
        is logged at INFO, not ERROR. A present-but-invalid artifact is a
        real problem and is logged as such.
        """
        if self._load_attempted:
            return self._artifact

        with self._lock:
            if self._load_attempted:
                return self._artifact

            try:
                self._artifact = load_model()
                self._load_error = None
            except FileNotFoundError as exc:
                self._artifact = None
                self._load_error = str(exc)
                logger.info(
                    "No volatility model artifact yet; using historical "
                    "volatility. (%s)", exc,
                )
            except ModelContractError as exc:
                self._artifact = None
                self._load_error = str(exc)
                logger.error("Volatility model rejected: %s", exc)
            except Exception as exc:  # noqa: BLE001
                self._artifact = None
                self._load_error = str(exc)
                logger.exception("Unexpected error loading volatility model")
            finally:
                self._load_attempted = True

        return self._artifact

    def reload_model(self) -> Dict[str, Any]:
        """
        Force a re-read of the artifact from disk.

        Call this after training so a freshly saved model is picked up
        without restarting the API.
        """
        with self._lock:
            self._artifact = None
            self._load_attempted = False
            self._load_error = None
            self._cache.clear()

        artifact = self._ensure_model()
        return {
            "model_loaded": artifact is not None,
            "error": self._load_error,
            "model": artifact.summary() if artifact else None,
        }

    def model_info(self) -> Dict[str, Any]:
        """Describe the currently loaded model, for the info endpoint."""
        artifact = self._ensure_model()
        return {
            "model_loaded": artifact is not None,
            "error": self._load_error,
            "horizon_days": HORIZON_DAYS,
            "fallback": "trailing 21-day realised volatility",
            "model": artifact.summary() if artifact else None,
        }

    @property
    def is_model_available(self) -> bool:
        return self._ensure_model() is not None

    # ── Forecasting ─────────────────────────────────────────────────

    def get_forecast(
        self,
        ticker: str,
        use_cache: bool = True,
    ) -> VolatilityForecast:
        """
        Forecast annualised volatility for `ticker`.

        Always returns a usable figure as long as price history can be
        loaded. Degradations are reported, not hidden.

        Raises:
            PriceDataError: no price history available from network or
                cache, so not even the historical fallback can be built.
        """
        key = ticker.upper()

        if use_cache:
            hit = self._cache.get(key)
            if hit and (time.monotonic() - hit[0]) < FORECAST_CACHE_TTL_SECONDS:
                return hit[1]

        # Price history is required for BOTH paths, so load it first and
        # let its failure be the only hard error.
        history = load_history(key, period=_INFERENCE_PERIOD)

        index_history = None
        try:
            index_history = load_history(INDEX_TICKER, period=_INFERENCE_PERIOD)
        except PriceDataError as exc:
            # Index features will be NaN, which blocks the ML path but
            # leaves the historical fallback intact.
            logger.warning("Index history unavailable (%s)", exc)

        historical_vol = self._historical_volatility(history)
        forecast = self._try_ml_forecast(key, history, index_history, historical_vol)

        if use_cache:
            self._cache[key] = (time.monotonic(), forecast)

        return forecast

    def _try_ml_forecast(
        self,
        ticker: str,
        history,
        index_history,
        historical_vol: Optional[float],
    ) -> VolatilityForecast:
        """Attempt the ML path, degrading to historical on any failure."""

        def fallback(reason: str) -> VolatilityForecast:
            if historical_vol is None:
                raise PriceDataError(
                    f"{ticker}: cannot produce any volatility estimate "
                    f"({reason}, and trailing realised volatility is unavailable)"
                )
            return VolatilityForecast(
                ticker=ticker,
                volatility=historical_vol,
                source=SOURCE_HISTORICAL,
                historical_volatility=historical_vol,
                fallback_reason=reason,
            )

        artifact = self._ensure_model()
        if artifact is None:
            return fallback(self._load_error or "No volatility model artifact loaded")

        try:
            features, as_of = latest_feature_row(history, index_history)
        except ValueError as exc:
            return fallback(f"Insufficient history for features: {exc}")

        try:
            predicted = artifact.predict(features)
        except Exception as exc:  # noqa: BLE001 - estimator can fail
            logger.exception("Volatility model prediction failed for %s", ticker)
            return fallback(f"Model prediction failed: {exc}")

        # Guard against a broken model. A regressor can emit negatives,
        # NaN, or absurd magnitudes, and feeding any of those into Monte
        # Carlo produces confident nonsense rather than an error.
        if not np.isfinite(predicted):
            return fallback(f"Model returned a non-finite value ({predicted})")

        if not (MIN_PLAUSIBLE_VOLATILITY <= predicted <= MAX_PLAUSIBLE_VOLATILITY):
            return fallback(
                f"Model returned {predicted:.4f}, outside the plausible range "
                f"[{MIN_PLAUSIBLE_VOLATILITY}, {MAX_PLAUSIBLE_VOLATILITY}]"
            )

        return VolatilityForecast(
            ticker=ticker,
            volatility=float(predicted),
            source=SOURCE_ML,
            predicted_volatility=float(predicted),
            historical_volatility=historical_vol,
            model_version=artifact.model_version,
            as_of=str(as_of.date()) if hasattr(as_of, "date") else str(as_of),
        )

    @staticmethod
    def _historical_volatility(history, window: int = HORIZON_DAYS) -> Optional[float]:
        """
        Trailing realised volatility, annualised — the fallback value.

        This is deliberately the same quantity as the `rv_21` feature and
        the same thing as the naive-persistence baseline in
        `app.ml.evaluation`. If the ML model cannot beat this number
        offline, the fallback is not a degradation at all, and that is
        worth knowing before shipping the feature.
        """
        close = history["close"]
        log_ret = np.log(close / close.shift(1)).dropna()

        if len(log_ret) < window:
            return None

        vol = float(log_ret.tail(window).std() * np.sqrt(TRADING_DAYS_PER_YEAR))
        return vol if np.isfinite(vol) and vol > 0 else None

    # ── Diagnostics ─────────────────────────────────────────────────

    def feature_snapshot(self, ticker: str) -> Dict[str, Any]:
        """
        Current feature values for a ticker.

        Useful when a prediction looks wrong: it shows what the model was
        actually given, which is usually where the problem is.
        """
        key = ticker.upper()
        history = load_history(key, period=_INFERENCE_PERIOD)

        try:
            index_history = load_history(INDEX_TICKER, period=_INFERENCE_PERIOD)
        except PriceDataError:
            index_history = None

        features, as_of = latest_feature_row(history, index_history)
        built = build_features(history, index_history)

        return {
            "ticker": key,
            "as_of": str(as_of.date()) if hasattr(as_of, "date") else str(as_of),
            "rows_available": int(len(built)),
            "complete_rows": int(len(built.dropna())),
            "features": {
                name: (None if not np.isfinite(v) else round(float(v), 6))
                for name, v in features.iloc[0].items()
            },
        }


# Module-level singleton, mirroring the existing `ollama_service` pattern
volatility_prediction_service = VolatilityPredictionService()
