"""
Trend Model Registry

The serving contract for the stock-trend classifier, enforced at load
time. It mirrors `app.ml.model_registry` for the volatility regressor, and
exists as a separate artifact type so the two can never be confused: a
volatility regressor loaded as a trend model would "work", returning
numbers that are not probabilities, with no exception raised.

The same rule applies as for volatility. A classifier over ~21 unlabelled
floats returns a plausible probability even when its columns arrive in the
wrong order, so the feature order is stored with the estimator and the
loader refuses to serve on any mismatch.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib

from app.ml.config import DEFAULT_TREND_MODEL_PATH, HORIZON_DAYS
from app.ml.features import FEATURE_NAMES
from app.ml.model_registry import ModelContractError
from app.ml.trend import TREND_TARGET_COLUMN

logger = logging.getLogger(__name__)

ARTIFACT_SCHEMA_VERSION = 1


@dataclass
class TrendModelArtifact:
    """A trained up/down classifier plus everything needed to serve it."""

    model: Any
    feature_names: List[str]
    model_version: str
    horizon_days: int = HORIZON_DAYS
    target: str = TREND_TARGET_COLUMN
    trained_at: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    notes: str = ""
    schema_version: int = ARTIFACT_SCHEMA_VERSION

    def predict_up_probability(self, features) -> float:
        """
        Probability that the stock closes higher at the horizon.

        Args:
            features: one-row DataFrame whose columns are
                `self.feature_names`

        The positive class is located through `classes_` rather than
        assumed to be column 1, so an estimator fitted with unusual label
        ordering still returns the probability of "up".
        """
        ordered = features[self.feature_names]
        proba = self.model.predict_proba(ordered)
        classes = list(getattr(self.model, "classes_", [0, 1]))
        return float(proba[0][classes.index(1)])

    def summary(self) -> Dict[str, Any]:
        """Serialisable description, for the model-info endpoint."""
        return {
            "model_version": self.model_version,
            "estimator": type(self.model).__name__,
            "horizon_days": self.horizon_days,
            "target": self.target,
            "trained_at": self.trained_at,
            "n_features": len(self.feature_names),
            "feature_names": self.feature_names,
            "metrics": self.metrics,
            "notes": self.notes,
            "schema_version": self.schema_version,
        }


def _check_classifier(model: Any) -> None:
    """Shared by save and load: the estimator must be a usable classifier."""
    if not hasattr(model, "predict_proba"):
        raise ModelContractError(
            f"{type(model).__name__} has no .predict_proba method; the trend "
            f"model must output probabilities. For an estimator without "
            f"native probabilities, wrap it in "
            f"sklearn.calibration.CalibratedClassifierCV."
        )
    classes = getattr(model, "classes_", None)
    if classes is not None and 1 not in list(classes):
        raise ModelContractError(
            f"Estimator classes are {list(classes)}; expected labels 0 and 1 "
            f"(1 = closes higher)."
        )


def save_trend_model(
    model: Any,
    model_version: str,
    metrics: Optional[Dict[str, float]] = None,
    notes: str = "",
    path: Optional[Path] = None,
    feature_names: Optional[List[str]] = None,
    horizon_days: int = HORIZON_DAYS,
) -> Path:
    """
    Persist a trained classifier in the format the API expects.

        from app.ml.trend import evaluate_trend_probabilities
        from app.ml.trend_registry import save_trend_model

        metrics = evaluate_trend_probabilities(y_test, p_test, y_train.mean())
        save_trend_model(
            model=fitted_classifier,
            model_version="logreg-v1",
            metrics=metrics,
            notes="L2 logistic regression on the 21 shared features.",
        )

    Always include the metrics from `evaluate_trend_probabilities`: the
    UI shows them next to the forecast, and `brier_skill_score` is how a
    viewer can tell whether the model beats the stock's own base rate.
    """
    _check_classifier(model)

    target_path = Path(path) if path else DEFAULT_TREND_MODEL_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    artifact = TrendModelArtifact(
        model=model,
        feature_names=list(feature_names) if feature_names else list(FEATURE_NAMES),
        model_version=model_version,
        horizon_days=horizon_days,
        trained_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        metrics=dict(metrics or {}),
        notes=notes,
    )

    joblib.dump(artifact, target_path)
    logger.info("Saved trend model '%s' to %s", model_version, target_path)
    return target_path


def load_trend_model(path: Optional[Path] = None, strict: bool = True) -> TrendModelArtifact:
    """
    Load and validate a saved trend artifact.

    Raises:
        FileNotFoundError: no artifact at `path`
        ModelContractError: unreadable, the wrong type (including a
            volatility artifact), or disagreeing with the running code
    """
    target_path = Path(path) if path else DEFAULT_TREND_MODEL_PATH

    if not target_path.exists():
        raise FileNotFoundError(f"No trend model artifact at {target_path}")

    try:
        artifact = joblib.load(target_path)
    except Exception as exc:  # noqa: BLE001 - unpickling fails many ways
        raise ModelContractError(f"Could not load artifact {target_path}: {exc}") from exc

    if not isinstance(artifact, TrendModelArtifact):
        raise ModelContractError(
            f"{target_path} contains {type(artifact).__name__}, expected "
            f"TrendModelArtifact. Save it with "
            f"app.ml.trend_registry.save_trend_model()."
        )

    _check_classifier(artifact.model)

    if strict and list(artifact.feature_names) != list(FEATURE_NAMES):
        trained, current = set(artifact.feature_names), set(FEATURE_NAMES)
        raise ModelContractError(
            "Feature mismatch between artifact and running code — refusing "
            "to serve.\n"
            f"  missing from artifact: {sorted(current - trained) or 'none'}\n"
            f"  unknown to this code:  {sorted(trained - current) or 'none'}\n"
            f"  order changed:         {trained == current}\n"
            "Retrain against the current app.ml.features.FEATURE_NAMES."
        )

    if strict and artifact.horizon_days != HORIZON_DAYS:
        raise ModelContractError(
            f"Artifact forecasts a {artifact.horizon_days}-day move but "
            f"config.HORIZON_DAYS is {HORIZON_DAYS}."
        )

    if strict and artifact.target != TREND_TARGET_COLUMN:
        raise ModelContractError(
            f"Artifact was trained on '{artifact.target}' but the running "
            f"code defines the target as '{TREND_TARGET_COLUMN}'."
        )

    logger.info(
        "Loaded trend model '%s' (%s, %d features)",
        artifact.model_version, type(artifact.model).__name__, len(artifact.feature_names),
    )
    return artifact
