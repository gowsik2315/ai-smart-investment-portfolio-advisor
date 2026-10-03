"""
Tests for volatility forecast metrics and baselines.

QLIKE gets the most attention here because it is the metric most easily
implemented wrong, and its asymmetry is the whole reason for preferring
it over RMSE in a risk tool.
"""

import numpy as np
import pandas as pd
import pytest

from app.ml.config import TARGET_COLUMN
from app.ml.evaluation import (
    compare_forecasts,
    fit_har,
    mae,
    naive_persistence,
    predict_har,
    qlike,
    r2,
    rmse,
    score,
)
from app.ml.features import build_training_table, chronological_split


class TestPointMetrics:

    def test_perfect_forecast_scores_zero_error(self):
        actual = np.array([0.1, 0.2, 0.3, 0.4])

        assert rmse(actual, actual) == pytest.approx(0.0)
        assert mae(actual, actual) == pytest.approx(0.0)
        assert qlike(actual, actual) == pytest.approx(0.0)
        assert r2(actual, actual) == pytest.approx(1.0)

    def test_rmse_penalises_concentrated_error_more_than_mae(self):
        """
        Same total absolute error, distributed differently: MAE cannot
        tell them apart, RMSE charges extra for concentrating it.
        """
        actual = np.array([0.2, 0.2, 0.2, 0.2])
        spread = np.array([0.3, 0.3, 0.3, 0.3])   # error 0.1 on every point
        spike = np.array([0.2, 0.2, 0.2, 0.6])    # error 0.4 on one point

        assert mae(actual, spread) == pytest.approx(mae(actual, spike))
        assert rmse(actual, spike) > rmse(actual, spread)

    def test_shape_mismatch_rejected(self):
        with pytest.raises(ValueError, match="Shape mismatch"):
            rmse(np.array([0.1, 0.2]), np.array([0.1]))

    def test_non_finite_pairs_dropped(self):
        actual = np.array([0.1, np.nan, 0.3])
        predicted = np.array([0.1, 0.2, 0.3])

        assert rmse(actual, predicted) == pytest.approx(0.0)

    def test_all_non_finite_raises(self):
        with pytest.raises(ValueError, match="No finite"):
            rmse(np.array([np.nan, np.nan]), np.array([0.1, 0.2]))

    def test_score_returns_every_metric(self):
        result = score(np.array([0.1, 0.2, 0.3]), np.array([0.12, 0.19, 0.31]))
        assert set(result) == {"rmse", "mae", "qlike", "r2"}


class TestQlike:

    def test_is_non_negative(self):
        actual = np.array([0.2, 0.25, 0.18, 0.3])
        for predicted in [actual * 0.5, actual * 1.5, actual * 0.9]:
            assert qlike(actual, predicted) >= 0

    def test_punishes_under_forecasting_harder_than_over_forecasting(self):
        """
        The defining property, and the reason this metric suits a risk
        tool: halving the true variance must cost more than doubling it.
        Understating tail risk is the expensive mistake.
        """
        actual = np.array([0.20, 0.20, 0.20, 0.20])

        under = qlike(actual, actual * 0.5)   # forecast half the volatility
        over = qlike(actual, actual * 2.0)    # forecast double

        assert under > over

    def test_rmse_by_contrast_is_symmetric_in_relative_terms(self):
        """
        Shows why QLIKE adds something: RMSE's absolute symmetry means a
        0.1 under-forecast and a 0.1 over-forecast score identically,
        even though their risk consequences differ sharply.
        """
        actual = np.array([0.30, 0.30])

        assert rmse(actual, actual - 0.1) == pytest.approx(rmse(actual, actual + 0.1))

    def test_non_positive_forecasts_are_dropped(self):
        actual = np.array([0.2, 0.2, 0.2])
        predicted = np.array([0.2, 0.0, -0.1])

        assert qlike(actual, predicted) == pytest.approx(0.0)

    def test_all_non_positive_forecasts_give_nan(self):
        assert np.isnan(qlike(np.array([0.2, 0.2]), np.array([0.0, -0.1])))

    def test_ranking_matches_pattons_formulation(self):
        """
        The zero-anchored form differs from Patton's `ln(h) + s/h` only
        by a term independent of the forecast, so both must rank a set of
        forecasts identically.
        """
        rng = np.random.default_rng(0)
        actual = rng.uniform(0.1, 0.5, 200)
        candidates = [actual * f for f in [0.6, 0.8, 1.0, 1.3, 1.8]]

        mine = [qlike(actual, c) for c in candidates]
        patton = [np.mean(np.log(c ** 2) + actual ** 2 / c ** 2) for c in candidates]

        assert np.argsort(mine).tolist() == np.argsort(patton).tolist()


class TestBaselines:

    def test_naive_persistence_is_trailing_realised_volatility(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        forecast = naive_persistence(table)

        pd.testing.assert_series_equal(
            forecast, table['rv_21'].rename('naive_persistence')
        )

    def test_naive_persistence_requires_rv_21(self):
        with pytest.raises(ValueError, match="rv_21"):
            naive_persistence(pd.DataFrame({'other': [1, 2, 3]}))

    def test_har_fits_and_predicts(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        train, test = chronological_split(table)

        model = fit_har(train, TARGET_COLUMN)
        predictions = predict_har(model, test)

        assert len(predictions) == len(test)
        assert predictions.notna().all()

    def test_har_requires_its_columns(self):
        with pytest.raises(ValueError):
            fit_har(pd.DataFrame({'rv_5': [1.0], TARGET_COLUMN: [1.0]}), TARGET_COLUMN)


class TestCompareForecasts:

    def test_scores_each_forecast_and_computes_improvement(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        train, test = chronological_split(table)
        actual = test[TARGET_COLUMN]

        result = compare_forecasts(
            actual=actual,
            forecasts={
                'naive_persistence': naive_persistence(test),
                'perfect': actual.copy(),
            },
        )

        assert set(result.index) == {'naive_persistence', 'perfect'}
        assert 'rmse_vs_baseline' in result.columns

        # A perfect forecast must win and show a 100% improvement
        assert result.loc['perfect', 'rmse'] == pytest.approx(0.0)
        assert result.loc['perfect', 'rmse_vs_baseline'] == pytest.approx(100.0)
        assert result.index[0] == 'perfect'  # sorted by qlike, best first

    def test_missing_baseline_omits_improvement_columns(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        _, test = chronological_split(table)

        result = compare_forecasts(
            actual=test[TARGET_COLUMN],
            forecasts={'something': test['rv_21']},
            baseline_name='not_present',
        )
        assert 'rmse_vs_baseline' not in result.columns

    def test_non_overlapping_forecast_is_skipped(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        _, test = chronological_split(table)

        disjoint = pd.Series(
            [0.2, 0.2],
            index=pd.to_datetime(['2099-01-01', '2099-01-02']),
        )
        result = compare_forecasts(
            actual=test[TARGET_COLUMN],
            forecasts={'good': test['rv_21'], 'disjoint': disjoint},
            baseline_name='good',
        )
        assert 'disjoint' not in result.index

    def test_no_scorable_forecast_raises(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        _, test = chronological_split(table)

        disjoint = pd.Series([0.2], index=pd.to_datetime(['2099-01-01']))
        with pytest.raises(ValueError, match="No forecast could be scored"):
            compare_forecasts(test[TARGET_COLUMN], {'disjoint': disjoint})
