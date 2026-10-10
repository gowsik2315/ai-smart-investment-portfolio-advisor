"""
Volatility Model Registry

Defines the contract between offline training and the live API, and
enforces it at load time.

The enforcement is the point. A volatility model is a regressor over ~21
unlabelled floats: hand it the same features in a different ORDER and it
will return a number, no exception raised, and that number will be
wrong. The only protection is to store the feature order alongside the
estimator and refuse to serve when it does not match what the running
code produces.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib

from app.ml.config import DEFAULT_MODEL_PATH, HORIZON_DAYS, MODELS_DIR, TARGET_COLUMN
from app.ml.features import FEATURE_NAMES

logger = logging.getLogger(__name__)

# Bump when the artifact dict layout itself changes
ARTIFACT_SCHEMA_VERSION = 1


class ModelContractError(RuntimeError):
    """Raised when an artifact does not satisfy the serving contract."""


@dataclass
class VolatilityModelArtifact:
    """A trained volatility model plus everything needed to serve it."""

    model: Any
    feature_names: List[str]
    model_version: str
    horizon_days: int = HORIZON_DAYS
    target: str = TARGET_COLUMN
    trained_at: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    notes: str = ""
    schema_version: int = ARTIFACT_SCHEMA_VERSION

    def predict(self, features) -> float:
        """
        Predict annualised volatility for a single feature row.

        Args:
            features: one-row DataFrame whose columns are
                `self.feature_names`

        Returns:
            The scalar forecast.
        """
        # Reindex rather than trust the caller's column order. Combined
        # with the load-time check this makes order errors impossible.
        ordered = features[self.feature_names]
        return float(self.model.predict(ordered)[0])

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


def save_model(
    model: Any,
    model_version: str,
    metrics: Optional[Dict[str, float]] = None,
    notes: str = "",
    path: Optional[Path] = None,
    feature_names: Optional[List[str]] = None,
    horizon_days: int = HORIZON_DAYS,
) -> Path:
    """
    Persist a trained model in the format the API expects.

    Call this at the end of training:

        from app.ml.model_registry import save_model
        save_model(
            model=fitted_estimator,
            model_version="ridge-har-v1",
            metrics={"rmse": 0.081, "mae": 0.058, "qlike": 0.214,
                     "baseline_rmse": 0.094},
            notes="HAR-style Ridge; beats naive persistence on RMSE and QLIKE.",
        )

    Args:
        model: any fitted estimator exposing `.predict(DataFrame)`
        model_version: short identifier, surfaced in API responses
        metrics: held-out scores. Include the baseline you compared
            against — a forecast with no baseline is not evidence.
        notes: free text shown by the model-info endpoint
        path: destination; defaults to `models/volatility_model.joblib`
        feature_names: defaults to the current `FEATURE_NAMES`. Pass
            explicitly only if you deliberately trained on a subset.
        horizon_days: forecast horizon the model was fitted for

    Returns:
        The path written.
    """
    if not hasattr(model, "predict"):
        raise ModelContractError(
            f"{type(model).__name__} has no .predict method; cannot be served."
        )

    target_path = Path(path) if path else DEFAULT_MODEL_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    artifact = VolatilityModelArtifact(
        model=model,
        feature_names=list(feature_names) if feature_names else list(FEATURE_NAMES),
        model_version=model_version,
        horizon_days=horizon_days,
        target=TARGET_COLUMN,
        trained_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        metrics=dict(metrics or {}),
        notes=notes,
        schema_version=ARTIFACT_SCHEMA_VERSION,
    )

    joblib.dump(artifact, target_path)
    logger.info("Saved volatility model '%s' to %s", model_version, target_path)

    return target_path


def load_model(path: Optional[Path] = None, strict: bool = True) -> VolatilityModelArtifact:
    """
    Load and validate a saved artifact.

    Args:
        path: artifact location; defaults to the configured path
        strict: when True, a feature-set mismatch raises. Set False only
            for offline inspection of an older artifact.

    Returns:
        The validated artifact.

    Raises:
        FileNotFoundError: no artifact at `path`
        ModelContractError: artifact is unreadable, the wrong type, or
            disagrees with the running feature definition
    """
    target_path = Path(path) if path else DEFAULT_MODEL_PATH

    if not target_path.exists():
        raise FileNotFoundError(f"No volatility model artifact at {target_path}")

    try:
        artifact = joblib.load(target_path)
    except Exception as exc:  # noqa: BLE001 - unpickling fails many ways
        raise ModelContractError(f"Could not load artifact {target_path}: {exc}") from exc

    if not isinstance(artifact, VolatilityModelArtifact):
        raise ModelContractError(
            f"{target_path} contains {type(artifact).__name__}, expected "
            f"VolatilityModelArtifact. Save it with "
            f"app.ml.model_registry.save_model()."
        )

    if not hasattr(artifact.model, "predict"):
        raise ModelContractError(
            f"Artifact estimator {type(artifact.model).__name__} has no .predict method."
        )

    # ── The check that matters ──────────────────────────────────────
    if strict and list(artifact.feature_names) != list(FEATURE_NAMES):
        trained = set(artifact.feature_names)
        current = set(FEATURE_NAMES)
        raise ModelContractError(
            "Feature mismatch between artifact and running code — refusing "
            "to serve.\n"
            f"  missing from artifact: {sorted(current - trained) or 'none'}\n"
            f"  unknown to this code:  {sorted(trained - current) or 'none'}\n"
            f"  order changed:         "
            f"{trained == current and list(artifact.feature_names) != list(FEATURE_NAMES)}\n"
            "Retrain against the current app.ml.features.FEATURE_NAMES."
        )

    if strict and artifact.horizon_days != HORIZON_DAYS:
        raise ModelContractError(
            f"Artifact forecasts {artifact.horizon_days}-day volatility but "
            f"config.HORIZON_DAYS is {HORIZON_DAYS}."
        )

    logger.info(
        "Loaded volatility model '%s' (%s, %d features)",
        artifact.model_version, type(artifact.model).__name__, len(artifact.feature_names),
    )

    return artifact


def list_artifacts() -> List[Dict[str, Any]]:
    """Enumerate artifacts in the models directory, for diagnostics."""
    if not MODELS_DIR.exists():
        return []

    # Imported here because trend_registry imports this module
    from app.ml.config import DEFAULT_TREND_MODEL_PATH
    from app.ml.trend_registry import TrendModelArtifact

    defaults = {
        DEFAULT_MODEL_PATH.resolve(): "volatility",
        DEFAULT_TREND_MODEL_PATH.resolve(): "trend",
    }

    rows = []
    for path in sorted(MODELS_DIR.glob("*.joblib")):
        row: Dict[str, Any] = {
            "file": path.name,
            "size_kb": round(path.stat().st_size / 1024, 1),
            "is_default": path.resolve() in defaults,
        }
        try:
            artifact = joblib.load(path)
            if isinstance(artifact, TrendModelArtifact):
                kind = "trend"
            elif isinstance(artifact, VolatilityModelArtifact):
                kind = "volatility"
            else:
                raise ModelContractError(
                    f"contains {type(artifact).__name__}, not a known model artifact"
                )
            row.update({
                "kind": kind,
                "model_version": artifact.model_version,
                "estimator": type(artifact.model).__name__,
                "trained_at": artifact.trained_at,
                "valid": list(artifact.feature_names) == list(FEATURE_NAMES),
            })
        except Exception as exc:  # noqa: BLE001 - diagnostics must not raise
            row.update({"error": str(exc), "valid": False})
        rows.append(row)

    return rows
