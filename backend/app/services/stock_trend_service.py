"""
Stock Trend Outlook Service

Produces, for one ticker, an honest account of what can and cannot be said
about the next 21 trading days:

    trend         where the stock is trending now (descriptive, not a forecast)
    probability   chance it closes higher at the horizon
    range         how far it may plausibly move, with no directional view

Fallback chain for the probability, mirroring the volatility service:
    1. ML classifier from the saved artifact        -> 'ml_predicted'
    2. The stock's own historical frequency of rising -> 'historical_base_rate'

The second is a statistic, not a prediction, and is labelled as such so the
UI never presents it as machine learning. The service always returns an
outlook when price history exists; only a missing or too-short history is
an error.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from app.ml.config import (
    HORIZON_DAYS,
    INDEX_TICKER,
    TREND_MIN_HISTORY_ROWS,
)
from app.ml.data import PriceDataError, load_history, validate_ticker
from app.ml.features import latest_feature_row
from app.ml.model_registry import ModelContractError
from app.ml.trend import base_rate_up, expected_range, technical_trend_signal
from app.ml.trend_registry import TrendModelArtifact, load_trend_model
from app.services.ml_prediction_service import (
    VolatilityForecast,
    volatility_prediction_service,
)

logger = logging.getLogger(__name__)

SOURCE_ML = "ml_predicted"
SOURCE_BASE_RATE = "historical_base_rate"

# yfinance period covering the 252-day feature lookback plus slack
_PERIOD = "3y"

# Trading days of closes returned for the chart
_CHART_DAYS = 126

DISCLAIMER = (
    "Educational analysis, not investment advice. Over a one-month window a "
    "stock's direction is close to unpredictable: judge the probability "
    "against the historical base rate shown beside it, not against 50%."
)


class StockTrendService:
    """Loads the trend classifier once and serves outlooks. Thread-safe."""

    def __init__(self) -> None:
        self._artifact: Optional[TrendModelArtifact] = None
        self._load_attempted = False
        self._load_error: Optional[str] = None
        self._lock = threading.Lock()

    # ── Model lifecycle ─────────────────────────────────────────────

    def _ensure_model(self) -> Optional[TrendModelArtifact]:
        """
        Load the artifact on first use. A missing artifact is the expected
        state before training and is logged at INFO; a present-but-invalid
        one is a real problem and is logged as an error.
        """
        if self._load_attempted:
            return self._artifact

        with self._lock:
            if self._load_attempted:
                return self._artifact
            try:
                self._artifact = load_trend_model()
                self._load_error = None
            except FileNotFoundError as exc:
                self._artifact, self._load_error = None, str(exc)
                logger.info("No trend model artifact yet; using the historical base rate. (%s)", exc)
            except ModelContractError as exc:
                self._artifact, self._load_error = None, str(exc)
                logger.error("Trend model rejected: %s", exc)
            except Exception as exc:  # noqa: BLE001
                self._artifact, self._load_error = None, str(exc)
                logger.exception("Unexpected error loading trend model")
            finally:
                self._load_attempted = True

        return self._artifact

    def reload_model(self) -> Dict[str, Any]:
        """Re-read the artifact from disk, e.g. after training."""
        with self._lock:
            self._artifact, self._load_attempted, self._load_error = None, False, None

        artifact = self._ensure_model()
        return {
            "model_loaded": artifact is not None,
            "error": self._load_error,
            "model": artifact.summary() if artifact else None,
        }

    def model_info(self) -> Dict[str, Any]:
        artifact = self._ensure_model()
        return {
            "model_loaded": artifact is not None,
            "error": self._load_error,
            "horizon_days": HORIZON_DAYS,
            "fallback": "the stock's own historical frequency of rising over 21 days",
            "model": artifact.summary() if artifact else None,
        }

    # ── Outlook ─────────────────────────────────────────────────────

    def get_outlook(self, ticker: str) -> Dict[str, Any]:
        """
        Build the outlook for `ticker`, fetching history from the cache or
        network.

        Raises:
            InvalidTickerError: `ticker` is not a plausible symbol
            PriceDataError: no price history obtainable
            ValueError: history exists but is too short to analyse
        """
        key = validate_ticker(ticker)
        history = load_history(key, period=_PERIOD)

        index_history = None
        try:
            index_history = load_history(INDEX_TICKER, period=_PERIOD)
        except PriceDataError as exc:
            # Blocks the ML path (the idx_* features) but nothing else
            logger.warning("Index history unavailable (%s)", exc)

        volatility = volatility_prediction_service.get_forecast(key)
        return self.outlook_from_history(key, history, index_history, volatility)

    def outlook_from_history(
        self,
        ticker: str,
        history: pd.DataFrame,
        index_history: Optional[pd.DataFrame],
        volatility: VolatilityForecast,
    ) -> Dict[str, Any]:
        """
        Assemble the outlook from data already in hand.

        Separate from `get_outlook` so the decision logic can be exercised
        without the network.
        """
        history = history.sort_index()

        if len(history) < TREND_MIN_HISTORY_ROWS:
            raise ValueError(
                f"{ticker}: only {len(history)} trading days of history; at "
                f"least {TREND_MIN_HISTORY_ROWS} are needed for an outlook."
            )

        last_close = float(history["close"].iloc[-1])
        base_rate = base_rate_up(history)
        if base_rate is None:
            raise ValueError(f"{ticker}: too few completed windows to compute a base rate.")

        probability, source, reason, model_version, metrics = self._probability(
            history, index_history, base_rate,
        )

        recent = history["close"].tail(_CHART_DAYS)

        return {
            "ticker": ticker,
            "as_of": str(history.index[-1].date()),
            "last_close": round(last_close, 2),
            "horizon_days": HORIZON_DAYS,
            "probability_up": round(probability, 4),
            "probability_source": source,
            "base_rate_up": round(base_rate, 4),
            "model_version": model_version,
            "fallback_reason": reason,
            "model_metrics": metrics,
            "trend": technical_trend_signal(history),
            "volatility": round(volatility.volatility, 6),
            "volatility_source": volatility.source,
            "volatility_fallback_reason": volatility.fallback_reason,
            "expected_range": expected_range(last_close, volatility.volatility),
            "recent_prices": [
                {"date": str(d.date()), "close": round(float(c), 2)}
                for d, c in recent.items()
            ],
            "disclaimer": DISCLAIMER,
        }

    def _probability(
        self,
        history: pd.DataFrame,
        index_history: Optional[pd.DataFrame],
        base_rate: float,
    ) -> Tuple[float, str, Optional[str], Optional[str], Optional[Dict[str, float]]]:
        """
        Pick the probability of a rise: the model's if it can be trusted,
        otherwise the base rate, with the reason recorded.

        Returns:
            (probability, source, fallback_reason, model_version, metrics)
        """

        def fallback(reason: str):
            return base_rate, SOURCE_BASE_RATE, reason, None, None

        artifact = self._ensure_model()
        if artifact is None:
            return fallback(self._load_error or "No trend model artifact loaded")

        try:
            features, _ = latest_feature_row(history, index_history)
        except ValueError as exc:
            return fallback(f"Insufficient history for features: {exc}")

        try:
            p = artifact.predict_up_probability(features)
        except Exception as exc:  # noqa: BLE001 - estimator can fail
            logger.exception("Trend model prediction failed")
            return fallback(f"Model prediction failed: {exc}")

        # A classifier can emit NaN or an out-of-range value if it is
        # broken or mis-wired; neither should reach a user as a probability.
        if not np.isfinite(p) or not 0.0 <= p <= 1.0:
            return fallback(f"Model returned an invalid probability ({p})")

        return float(p), SOURCE_ML, None, artifact.model_version, dict(artifact.metrics)


stock_trend_service = StockTrendService()
