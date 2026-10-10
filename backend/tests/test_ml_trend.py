"""
Tests for the stock-trend outlook.

The module predicts the probability a stock closes higher in 21 trading
days. Three properties matter most and are pinned down here:

1. The label is built strictly from the future and never leaks into the
   training features (and the forward return is not left in the table
   where a careless "all columns except the target" would pick it up).

2. The classifier artifact is refused unless it satisfies the contract: a
   volatility regressor loaded as a trend model would return numbers that
   are not probabilities, with no exception raised.

3. The service always returns an outlook when history exists, and says
   truthfully whether the probability is a model output or just the
   stock's own base rate.
"""

import math

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.ml.config import HORIZON_DAYS, TREND_MIN_HISTORY_ROWS
from app.ml.features import FEATURE_NAMES, chronological_split
from app.ml.model_registry import ModelContractError, save_model
from app.ml.trend import (
    TREND_RETURN_COLUMN,
    TREND_TARGET_COLUMN,
    base_rate_up,
    build_trend_target,
    build_trend_training_table,
    evaluate_trend_probabilities,
    expected_range,
    technical_trend_signal,
)
from app.ml.trend_registry import (
    TrendModelArtifact,
    load_trend_model,
    save_trend_model,
)
from app.services.ml_prediction_service import SOURCE_HISTORICAL, VolatilityForecast
from app.services.stock_trend_service import (
    SOURCE_BASE_RATE,
    SOURCE_ML,
    StockTrendService,
)
from tests.conftest import make_ohlcv


def trending_frame(n: int, daily_log_drift: float) -> pd.DataFrame:
    """Deterministic OHLCV drifting at a constant daily log rate."""
    close = 100.0 * np.exp(daily_log_drift * np.arange(n))
    return pd.DataFrame(
        {
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": np.full(n, 1_000_000),
        },
        index=pd.DatetimeIndex(pd.bdate_range("2021-01-01", periods=n), name="date"),
    )


class StubClassifier:
    """Minimal estimator with a configurable probability and class order."""

    def __init__(self, p_up, classes=(0, 1)):
        self.p_up = p_up
        self.classes_ = np.array(classes)

    def predict_proba(self, X):
        if list(self.classes_) == [0, 1]:
            return np.array([[1 - self.p_up, self.p_up]])
        return np.array([[self.p_up, 1 - self.p_up]])


@pytest.fixture
def table(ohlcv, index_ohlcv):
    return build_trend_training_table(ohlcv, index_ohlcv)


@pytest.fixture
def fitted_classifier(table):
    X = table[FEATURE_NAMES]
    y = table[TREND_TARGET_COLUMN].astype(int)
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)


@pytest.fixture
def volatility():
    return VolatilityForecast(
        ticker="TEST.NS", volatility=0.25, source=SOURCE_HISTORICAL,
        historical_volatility=0.25, fallback_reason="no volatility model",
    )


def service_with(artifact=None, error="No artifact"):
    service = StockTrendService()
    service._load_attempted = True
    service._artifact = artifact
    service._load_error = None if artifact else error
    return service


# ── Target ───────────────────────────────────────────────────────────

class TestTarget:

    def test_label_matches_independent_computation(self, ohlcv):
        target = build_trend_target(ohlcv)
        close = ohlcv["close"].to_numpy()

        for t in (0, 50, 300, 700, 878):
            expected = 1.0 if math.log(close[t + HORIZON_DAYS] / close[t]) > 0 else 0.0
            assert target[TREND_TARGET_COLUMN].iloc[t] == expected

    def test_last_horizon_rows_have_no_label(self, ohlcv):
        target = build_trend_target(ohlcv)
        assert target[TREND_TARGET_COLUMN].tail(HORIZON_DAYS).isna().all()
        assert target[TREND_TARGET_COLUMN].iloc[-HORIZON_DAYS - 1:-HORIZON_DAYS].notna().all()

    def test_label_depends_only_on_the_window_it_covers(self, ohlcv):
        """Removing everything after t+horizon must not change the label at t."""
        t = 400
        full = build_trend_target(ohlcv)[TREND_TARGET_COLUMN].iloc[t]
        truncated = build_trend_target(ohlcv.iloc[: t + HORIZON_DAYS + 1])[TREND_TARGET_COLUMN].iloc[t]
        assert full == truncated

    def test_rising_series_is_always_labelled_up(self):
        target = build_trend_target(trending_frame(200, 0.002))[TREND_TARGET_COLUMN].dropna()
        assert (target == 1.0).all()

    def test_falling_series_is_always_labelled_down(self):
        target = build_trend_target(trending_frame(200, -0.002))[TREND_TARGET_COLUMN].dropna()
        assert (target == 0.0).all()


class TestTrainingTable:

    def test_columns_are_features_plus_target_only(self, table):
        assert list(table.columns) == FEATURE_NAMES + [TREND_TARGET_COLUMN]

    def test_forward_return_is_not_in_the_table(self, table):
        """
        The label is derived from it. Leaving it in would let a training
        script that selects 'every column except the target' feed the model
        its own answer.
        """
        assert TREND_RETURN_COLUMN not in table.columns

    def test_labels_are_binary_and_rows_complete(self, table):
        assert set(table[TREND_TARGET_COLUMN].unique()) <= {0.0, 1.0}
        assert not table.isna().any().any()

    def test_ticker_column_added_on_request(self, ohlcv, index_ohlcv):
        t = build_trend_training_table(ohlcv, index_ohlcv, ticker="TEST.NS")
        assert (t["ticker"] == "TEST.NS").all()

    def test_chronological_split_keeps_the_embargo(self, table):
        train, test = chronological_split(table)
        dates = table.index.unique().sort_values()
        between = dates[(dates > train.index.max()) & (dates < test.index.min())]
        assert len(between) >= HORIZON_DAYS


# ── Descriptive trend ────────────────────────────────────────────────

class TestTechnicalSignal:

    def test_steady_uptrend_is_bullish_on_every_signal(self):
        result = technical_trend_signal(trending_frame(300, 0.002))
        assert result["label"] == "Bullish"
        assert result["score"] == 1.0
        assert all(s["bullish"] for s in result["signals"])
        assert len(result["signals"]) == 4

    def test_steady_downtrend_is_bearish_on_every_signal(self):
        result = technical_trend_signal(trending_frame(300, -0.002))
        assert result["label"] == "Bearish"
        assert result["score"] == -1.0
        assert not any(s["bullish"] for s in result["signals"])

    def test_short_history_omits_signals_it_cannot_compute(self):
        names = {s["name"] for s in technical_trend_signal(trending_frame(60, 0.001))["signals"]}
        assert names == {"price_vs_sma50", "momentum_21d"}

    @pytest.mark.parametrize("seed", range(6))
    def test_label_always_agrees_with_score(self, seed):
        result = technical_trend_signal(make_ohlcv(n_days=400, seed=seed))
        expected = "Bullish" if result["score"] >= 0.5 else "Bearish" if result["score"] <= -0.5 else "Neutral"
        assert result["label"] == expected
        assert -1.0 <= result["score"] <= 1.0

    def test_rsi_is_reported_but_not_scored(self):
        result = technical_trend_signal(trending_frame(300, 0.002))
        assert result["rsi_14"] == 100.0
        assert result["rsi_state"] == "overbought"
        assert "rsi" not in {s["name"] for s in result["signals"]}


# ── Baseline ─────────────────────────────────────────────────────────

class TestBaseRate:

    def test_always_rising_is_one(self):
        assert base_rate_up(trending_frame(300, 0.002)) == 1.0

    def test_always_falling_is_zero(self):
        assert base_rate_up(trending_frame(300, -0.002)) == 0.0

    def test_too_few_windows_returns_none(self):
        assert base_rate_up(trending_frame(70, 0.002)) is None

    def test_mixed_series_lies_strictly_between(self, ohlcv):
        assert 0.0 < base_rate_up(ohlcv) < 1.0


# ── Expected range ───────────────────────────────────────────────────

class TestExpectedRange:

    def test_has_one_point_per_day_including_day_zero(self):
        path = expected_range(1000.0, 0.25)
        assert [p["day"] for p in path] == list(range(HORIZON_DAYS + 1))

    def test_day_zero_has_no_width(self):
        p0 = expected_range(1000.0, 0.25)[0]
        assert p0["lower_95"] == p0["upper_95"] == p0["median"] == 1000.0

    def test_zero_volatility_collapses_every_band(self):
        for p in expected_range(1000.0, 0.0):
            assert p["lower_95"] == p["upper_95"] == 1000.0

    def test_width_grows_with_the_square_root_of_time(self):
        path = expected_range(1000.0, 0.30)
        spread = lambda k: math.log(path[k]["upper_68"] / 1000.0)
        assert spread(16) == pytest.approx(2 * spread(4), rel=1e-3)

    def test_horizon_band_matches_the_closed_form(self):
        sigma = 0.25
        last = expected_range(1000.0, sigma)[-1]
        assert last["upper_68"] == pytest.approx(1000.0 * math.exp(sigma * math.sqrt(21 / 252)), abs=0.01)

    def test_95_band_contains_the_68_band(self):
        for p in expected_range(1000.0, 0.25):
            assert p["lower_95"] <= p["lower_68"] <= p["median"] <= p["upper_68"] <= p["upper_95"]

    def test_bands_are_symmetric_in_log_space(self):
        p = expected_range(1000.0, 0.40)[-1]
        assert math.log(p["upper_95"] / 1000.0) == pytest.approx(-math.log(p["lower_95"] / 1000.0), abs=1e-3)

    def test_lower_bound_stays_positive_at_extreme_volatility(self):
        assert all(p["lower_95"] > 0 for p in expected_range(1000.0, 4.0))

    @pytest.mark.parametrize("price, sigma", [(0, 0.2), (-5, 0.2), (float("nan"), 0.2),
                                              (100, -0.1), (100, float("inf"))])
    def test_invalid_inputs_are_rejected(self, price, sigma):
        with pytest.raises(ValueError):
            expected_range(price, sigma)


# ── Scoring ──────────────────────────────────────────────────────────

class TestEvaluation:

    def test_predicting_the_base_rate_has_zero_skill(self):
        y = np.array([1, 1, 0, 1, 0, 1, 1, 0, 1, 1], dtype=float)
        result = evaluate_trend_probabilities(y, np.full(10, 0.6), train_base_rate=0.6)
        assert result["brier_skill_score"] == pytest.approx(0.0, abs=1e-9)

    def test_good_predictions_beat_the_baseline(self):
        y = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=float)
        p = np.where(y == 1, 0.9, 0.1)
        result = evaluate_trend_probabilities(y, p, train_base_rate=0.5)
        assert result["brier_skill_score"] > 0.5
        assert result["accuracy"] == 1.0
        assert result["roc_auc"] == 1.0

    def test_confident_wrong_predictions_score_below_the_baseline(self):
        y = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=float)
        p = np.where(y == 1, 0.1, 0.9)
        assert evaluate_trend_probabilities(y, p, 0.5)["brier_skill_score"] < 0

    def test_accuracy_baseline_is_the_train_majority_class(self):
        """Always saying 'up' scores well in a market that mostly rises."""
        y = np.array([1, 1, 1, 0], dtype=float)
        result = evaluate_trend_probabilities(y, np.full(4, 0.5), train_base_rate=0.7)
        assert result["baseline_accuracy"] == 0.75

    def test_single_class_test_set_has_no_auc(self):
        result = evaluate_trend_probabilities(np.ones(5), np.full(5, 0.6), 0.6)
        assert result["roc_auc"] is None

    @pytest.mark.parametrize("y, p, base", [
        ([1, 0], [0.5], 0.5),
        ([], [], 0.5),
        ([1, 0], [0.5, 0.5], 1.5),
    ])
    def test_malformed_inputs_are_rejected(self, y, p, base):
        with pytest.raises(ValueError):
            evaluate_trend_probabilities(y, p, base)


# ── Artifact contract ────────────────────────────────────────────────

class TestTrendRegistry:

    def test_round_trip_preserves_metadata_and_predicts_a_probability(
        self, fitted_classifier, tmp_path, ohlcv, index_ohlcv
    ):
        from app.ml.features import latest_feature_row
        path = tmp_path / "trend.joblib"
        save_trend_model(fitted_classifier, "lr-v1", metrics={"brier": 0.24}, notes="t", path=path)
        loaded = load_trend_model(path)

        row, _ = latest_feature_row(ohlcv, index_ohlcv)
        p = loaded.predict_up_probability(row)

        assert loaded.model_version == "lr-v1"
        assert loaded.metrics == {"brier": 0.24}
        assert loaded.feature_names == FEATURE_NAMES
        assert 0.0 <= p <= 1.0

    def test_prediction_is_insensitive_to_column_order(
        self, fitted_classifier, tmp_path, ohlcv, index_ohlcv
    ):
        from app.ml.features import latest_feature_row
        path = tmp_path / "trend.joblib"
        save_trend_model(fitted_classifier, "lr-v1", path=path)
        loaded = load_trend_model(path)

        row, _ = latest_feature_row(ohlcv, index_ohlcv)
        shuffled = row[list(reversed(FEATURE_NAMES))]
        assert loaded.predict_up_probability(row) == pytest.approx(loaded.predict_up_probability(shuffled))

    def test_positive_class_is_found_through_classes_not_assumed(self, ohlcv, index_ohlcv):
        """classes_ = [1, 0] puts 'up' in column 0; the answer is still P(up)."""
        from app.ml.features import latest_feature_row
        row, _ = latest_feature_row(ohlcv, index_ohlcv)
        artifact = TrendModelArtifact(
            model=StubClassifier(0.8, classes=(1, 0)),
            feature_names=FEATURE_NAMES, model_version="stub",
        )
        assert artifact.predict_up_probability(row) == pytest.approx(0.8)

    def test_feature_mismatch_is_refused(self, fitted_classifier, tmp_path):
        path = tmp_path / "trend.joblib"
        save_trend_model(fitted_classifier, "subset", feature_names=FEATURE_NAMES[:10], path=path)
        with pytest.raises(ModelContractError, match="Feature mismatch"):
            load_trend_model(path)

    def test_reordered_features_are_refused(self, fitted_classifier, tmp_path):
        path = tmp_path / "trend.joblib"
        save_trend_model(fitted_classifier, "rev", feature_names=list(reversed(FEATURE_NAMES)), path=path)
        with pytest.raises(ModelContractError, match="Feature mismatch"):
            load_trend_model(path)

    def test_horizon_mismatch_is_refused(self, fitted_classifier, tmp_path):
        path = tmp_path / "trend.joblib"
        save_trend_model(fitted_classifier, "h5", horizon_days=5, path=path)
        with pytest.raises(ModelContractError, match="move but"):
            load_trend_model(path)

    def test_regressor_without_probabilities_is_refused_at_save(self, tmp_path, table):
        reg = LinearRegression().fit(table[FEATURE_NAMES], table[TREND_TARGET_COLUMN])
        with pytest.raises(ModelContractError, match="predict_proba"):
            save_trend_model(reg, "reg", path=tmp_path / "x.joblib")

    def test_estimator_without_the_up_class_is_refused(self, tmp_path):
        with pytest.raises(ModelContractError, match="expected labels 0 and 1"):
            save_trend_model(StubClassifier(0.5, classes=(0, 2)), "bad", path=tmp_path / "x.joblib")

    def test_a_volatility_artifact_is_not_accepted_as_a_trend_model(self, tmp_path, table):
        """The mix-up this separate artifact type exists to prevent."""
        reg = LinearRegression().fit(table[FEATURE_NAMES], table[TREND_TARGET_COLUMN])
        path = tmp_path / "vol.joblib"
        save_model(reg, "vol-v1", path=path)
        with pytest.raises(ModelContractError, match="expected TrendModelArtifact"):
            load_trend_model(path)

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_trend_model(tmp_path / "nope.joblib")

    def test_cache_status_listing_recognises_both_artifact_kinds(
        self, fitted_classifier, tmp_path, monkeypatch, table
    ):
        import app.ml.model_registry as registry
        monkeypatch.setattr(registry, "MODELS_DIR", tmp_path)

        reg = LinearRegression().fit(table[FEATURE_NAMES], table["rsi_14"])
        save_model(reg, "vol-v1", path=tmp_path / "volatility_model.joblib")
        save_trend_model(fitted_classifier, "trend-v1", path=tmp_path / "trend_model.joblib")

        rows = {r["file"]: r for r in registry.list_artifacts()}
        assert rows["volatility_model.joblib"]["kind"] == "volatility"
        assert rows["trend_model.joblib"]["kind"] == "trend"
        assert all(r["valid"] for r in rows.values())


# ── Service ──────────────────────────────────────────────────────────

class TestStockTrendService:

    def test_without_a_model_the_base_rate_is_used_and_labelled(
        self, ohlcv, index_ohlcv, volatility
    ):
        out = service_with(None, "No artifact").outlook_from_history(
            "TEST.NS", ohlcv, index_ohlcv, volatility)

        assert out["probability_source"] == SOURCE_BASE_RATE
        assert out["probability_up"] == pytest.approx(out["base_rate_up"])
        assert "No artifact" in out["fallback_reason"]
        assert out["model_version"] is None
        assert out["model_metrics"] is None

    def test_with_a_model_its_probability_and_metrics_are_returned(
        self, fitted_classifier, ohlcv, index_ohlcv, volatility
    ):
        artifact = TrendModelArtifact(
            model=fitted_classifier, feature_names=FEATURE_NAMES,
            model_version="lr-v1", metrics={"brier": 0.24, "brier_skill_score": 0.01},
        )
        out = service_with(artifact).outlook_from_history("TEST.NS", ohlcv, index_ohlcv, volatility)

        assert out["probability_source"] == SOURCE_ML
        assert out["model_version"] == "lr-v1"
        assert out["fallback_reason"] is None
        assert out["model_metrics"]["brier_skill_score"] == 0.01
        assert 0.0 <= out["probability_up"] <= 1.0

    @pytest.mark.parametrize("bad", [float("nan"), 1.5, -0.2, float("inf")])
    def test_an_invalid_probability_falls_back(self, bad, ohlcv, index_ohlcv, volatility):
        artifact = TrendModelArtifact(
            model=StubClassifier(bad), feature_names=FEATURE_NAMES, model_version="bad")
        out = service_with(artifact).outlook_from_history("TEST.NS", ohlcv, index_ohlcv, volatility)

        assert out["probability_source"] == SOURCE_BASE_RATE
        assert out["probability_up"] == pytest.approx(out["base_rate_up"])
        assert "invalid probability" in out["fallback_reason"]

    def test_a_model_that_raises_falls_back(self, ohlcv, index_ohlcv, volatility):
        class Exploding:
            classes_ = np.array([0, 1])
            def predict_proba(self, X):
                raise RuntimeError("boom")

        artifact = TrendModelArtifact(model=Exploding(), feature_names=FEATURE_NAMES, model_version="x")
        out = service_with(artifact).outlook_from_history("TEST.NS", ohlcv, index_ohlcv, volatility)

        assert out["probability_source"] == SOURCE_BASE_RATE
        assert "boom" in out["fallback_reason"]

    def test_history_too_short_for_features_falls_back_not_fails(
        self, fitted_classifier, index_ohlcv, volatility
    ):
        """130 rows clears the minimum but not the 252-day feature lookback."""
        artifact = TrendModelArtifact(
            model=fitted_classifier, feature_names=FEATURE_NAMES, model_version="v1")
        out = service_with(artifact).outlook_from_history(
            "TEST.NS", make_ohlcv(n_days=130), index_ohlcv, volatility)

        assert out["probability_source"] == SOURCE_BASE_RATE
        assert "Insufficient history" in out["fallback_reason"]

    def test_history_below_the_minimum_is_an_error(self, index_ohlcv, volatility):
        with pytest.raises(ValueError, match="trading days of history"):
            service_with(None).outlook_from_history(
                "TEST.NS", make_ohlcv(n_days=TREND_MIN_HISTORY_ROWS - 1), index_ohlcv, volatility)

    def test_missing_index_history_blocks_only_the_model_path(self, fitted_classifier, ohlcv, volatility):
        artifact = TrendModelArtifact(
            model=fitted_classifier, feature_names=FEATURE_NAMES, model_version="v1")
        out = service_with(artifact).outlook_from_history("TEST.NS", ohlcv, None, volatility)

        assert out["probability_source"] == SOURCE_BASE_RATE
        assert out["trend"]["label"] in {"Bullish", "Neutral", "Bearish"}

    def test_outlook_is_complete_and_internally_consistent(self, ohlcv, index_ohlcv, volatility):
        out = service_with(None).outlook_from_history("TEST.NS", ohlcv, index_ohlcv, volatility)

        assert out["as_of"] == str(ohlcv.index[-1].date())
        assert out["last_close"] == pytest.approx(ohlcv["close"].iloc[-1], abs=0.01)
        assert out["horizon_days"] == HORIZON_DAYS
        assert len(out["expected_range"]) == HORIZON_DAYS + 1
        assert out["expected_range"][0]["median"] == out["last_close"]
        assert len(out["recent_prices"]) == 126
        assert out["recent_prices"][-1]["close"] == out["last_close"]
        assert out["volatility"] == 0.25
        assert out["volatility_source"] == SOURCE_HISTORICAL
        assert out["disclaimer"]

    def test_range_uses_the_supplied_volatility(self, ohlcv, index_ohlcv, volatility):
        out = service_with(None).outlook_from_history("TEST.NS", ohlcv, index_ohlcv, volatility)
        expected = out["last_close"] * math.exp(0.25 * math.sqrt(21 / 252))
        assert out["expected_range"][-1]["upper_68"] == pytest.approx(expected, abs=0.01)

    def test_model_info_reports_no_model_before_training(self):
        info = service_with(None, "No trend model artifact").model_info()
        assert info["model_loaded"] is False
        assert info["model"] is None
        assert "No trend model artifact" in info["error"]
