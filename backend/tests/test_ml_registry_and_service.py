"""
Tests for the model artifact contract and the prediction service.

Two behaviours matter most:

1. A model whose feature set disagrees with the running code must be
   REFUSED, not served. Serving it would silently produce wrong numbers,
   since a regressor given 21 floats in the wrong order still returns a
   plausible-looking float.

2. The prediction service must always yield a usable sigma when price
   history exists — no model, a broken model, or an absurd prediction all
   degrade to trailing realised volatility rather than failing or, worse,
   passing nonsense into Monte Carlo.
"""

import numpy as np
import pytest
from sklearn.linear_model import LinearRegression

from app.ml.features import FEATURE_NAMES, build_training_table
from app.ml.config import TARGET_COLUMN
from app.ml.model_registry import (
    ModelContractError,
    VolatilityModelArtifact,
    load_model,
    save_model,
)
from app.services.ml_prediction_service import (
    SOURCE_HISTORICAL,
    SOURCE_ML,
    VolatilityPredictionService,
)


@pytest.fixture
def fitted_model(ohlcv, index_ohlcv):
    """A real (if unimpressive) model fitted on synthetic data."""
    table = build_training_table(ohlcv, index_ohlcv)
    return LinearRegression().fit(table[FEATURE_NAMES], table[TARGET_COLUMN])


@pytest.fixture
def artifact_path(tmp_path):
    return tmp_path / "volatility_model.joblib"


class TestArtifactRoundTrip:

    def test_save_then_load_preserves_metadata(self, fitted_model, artifact_path):
        save_model(
            model=fitted_model,
            model_version="test-v1",
            metrics={"rmse": 0.05, "qlike": 0.2},
            notes="unit test",
            path=artifact_path,
        )
        loaded = load_model(artifact_path)

        assert loaded.model_version == "test-v1"
        assert loaded.feature_names == FEATURE_NAMES
        assert loaded.metrics["rmse"] == 0.05
        assert loaded.notes == "unit test"
        assert loaded.trained_at is not None

    def test_loaded_model_predicts(self, fitted_model, artifact_path, ohlcv, index_ohlcv):
        save_model(fitted_model, "test-v1", path=artifact_path)
        loaded = load_model(artifact_path)

        from app.ml.features import latest_feature_row
        row, _ = latest_feature_row(ohlcv, index_ohlcv)
        prediction = loaded.predict(row)

        assert isinstance(prediction, float)
        assert np.isfinite(prediction)

    def test_predict_is_order_insensitive(self, fitted_model, artifact_path,
                                          ohlcv, index_ohlcv):
        """
        The artifact reindexes to its own feature order, so a caller
        handing columns over in a different order still gets the right
        answer rather than a silently wrong one.
        """
        save_model(fitted_model, "test-v1", path=artifact_path)
        loaded = load_model(artifact_path)

        from app.ml.features import latest_feature_row
        row, _ = latest_feature_row(ohlcv, index_ohlcv)
        shuffled = row[list(reversed(FEATURE_NAMES))]

        assert loaded.predict(row) == pytest.approx(loaded.predict(shuffled))

    def test_summary_is_serialisable(self, fitted_model, artifact_path):
        save_model(fitted_model, "test-v1", path=artifact_path)
        summary = load_model(artifact_path).summary()

        import json
        json.dumps(summary)  # must not raise
        assert summary["n_features"] == len(FEATURE_NAMES)


class TestContractEnforcement:

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_model(tmp_path / "nope.joblib")

    def test_feature_mismatch_is_refused(self, fitted_model, artifact_path):
        """The check that prevents silent wrongness."""
        save_model(
            fitted_model, "subset-v1",
            feature_names=FEATURE_NAMES[:10],
            path=artifact_path,
        )
        with pytest.raises(ModelContractError, match="Feature mismatch"):
            load_model(artifact_path)

    def test_reordered_features_are_refused(self, fitted_model, artifact_path):
        """Same names, different order — must still be rejected."""
        save_model(
            fitted_model, "reordered-v1",
            feature_names=list(reversed(FEATURE_NAMES)),
            path=artifact_path,
        )
        with pytest.raises(ModelContractError, match="Feature mismatch"):
            load_model(artifact_path)

    def test_horizon_mismatch_is_refused(self, fitted_model, artifact_path):
        save_model(fitted_model, "wrong-horizon", horizon_days=5, path=artifact_path)
        with pytest.raises(ModelContractError, match="volatility but"):
            load_model(artifact_path)

    def test_bare_pickle_is_refused(self, fitted_model, artifact_path):
        """A plain joblib.dump of an estimator lacks the feature list."""
        import joblib
        joblib.dump(fitted_model, artifact_path)

        with pytest.raises(ModelContractError, match="expected VolatilityModelArtifact"):
            load_model(artifact_path)

    def test_object_without_predict_is_refused_at_save(self):
        with pytest.raises(ModelContractError, match="no .predict method"):
            save_model(model="not a model", model_version="bad")

    def test_strict_false_allows_inspection_of_mismatched_artifact(
        self, fitted_model, artifact_path
    ):
        save_model(fitted_model, "subset", feature_names=FEATURE_NAMES[:5],
                   path=artifact_path)
        loaded = load_model(artifact_path, strict=False)
        assert loaded.model_version == "subset"


class TestPredictionServiceFallback:
    """
    The service is exercised with injected history so these tests stay
    offline. `_try_ml_forecast` is the decision point under test.
    """

    def test_falls_back_when_no_model_is_loaded(self, ohlcv, index_ohlcv):
        service = VolatilityPredictionService()
        service._load_attempted = True
        service._artifact = None
        service._load_error = "No artifact"

        historical = service._historical_volatility(ohlcv)
        forecast = service._try_ml_forecast("TEST.NS", ohlcv, index_ohlcv, historical)

        assert forecast.source == SOURCE_HISTORICAL
        assert forecast.volatility == historical
        assert forecast.predicted_volatility is None
        assert "No artifact" in forecast.fallback_reason

    def test_uses_model_when_available(self, fitted_model, artifact_path,
                                      ohlcv, index_ohlcv):
        save_model(fitted_model, "test-v1", path=artifact_path)

        service = VolatilityPredictionService()
        service._load_attempted = True
        service._artifact = load_model(artifact_path)

        historical = service._historical_volatility(ohlcv)
        forecast = service._try_ml_forecast("TEST.NS", ohlcv, index_ohlcv, historical)

        assert forecast.source == SOURCE_ML
        assert forecast.model_version == "test-v1"
        assert forecast.predicted_volatility == forecast.volatility
        assert forecast.historical_volatility == historical

    @pytest.mark.parametrize("bad_value", [-0.5, 0.0, 99.0, float("nan"), float("inf")])
    def test_implausible_prediction_falls_back(self, bad_value, ohlcv, index_ohlcv):
        """
        A regressor can emit a negative, zero, NaN or absurd volatility.
        Any of those reaching Monte Carlo would yield confident nonsense,
        so they must be rejected in favour of the historical estimate.
        """
        class BadModel:
            def predict(self, X):
                return np.array([bad_value])

        service = VolatilityPredictionService()
        service._load_attempted = True
        service._artifact = VolatilityModelArtifact(
            model=BadModel(), feature_names=FEATURE_NAMES, model_version="bad",
        )

        historical = service._historical_volatility(ohlcv)
        forecast = service._try_ml_forecast("TEST.NS", ohlcv, index_ohlcv, historical)

        assert forecast.source == SOURCE_HISTORICAL
        assert forecast.volatility == historical
        assert forecast.fallback_reason

    def test_raising_model_falls_back(self, ohlcv, index_ohlcv):
        class ExplodingModel:
            def predict(self, X):
                raise RuntimeError("boom")

        service = VolatilityPredictionService()
        service._load_attempted = True
        service._artifact = VolatilityModelArtifact(
            model=ExplodingModel(), feature_names=FEATURE_NAMES, model_version="boom",
        )

        historical = service._historical_volatility(ohlcv)
        forecast = service._try_ml_forecast("TEST.NS", ohlcv, index_ohlcv, historical)

        assert forecast.source == SOURCE_HISTORICAL
        assert "boom" in forecast.fallback_reason

    def test_short_history_falls_back(self, short_ohlcv, index_ohlcv, fitted_model):
        service = VolatilityPredictionService()
        service._load_attempted = True
        service._artifact = VolatilityModelArtifact(
            model=fitted_model, feature_names=FEATURE_NAMES, model_version="v1",
        )

        historical = service._historical_volatility(short_ohlcv)
        forecast = service._try_ml_forecast("TEST.NS", short_ohlcv, index_ohlcv, historical)

        assert forecast.source == SOURCE_HISTORICAL
        assert "Insufficient history" in forecast.fallback_reason

    def test_historical_volatility_is_annualised_and_positive(self, ohlcv):
        service = VolatilityPredictionService()
        vol = service._historical_volatility(ohlcv)

        assert vol is not None
        assert 0 < vol < 3.0

    def test_historical_volatility_none_when_too_short(self):
        from tests.conftest import make_ohlcv
        service = VolatilityPredictionService()
        assert service._historical_volatility(make_ohlcv(n_days=5)) is None
