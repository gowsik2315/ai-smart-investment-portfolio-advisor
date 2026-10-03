"""
Tests for volatility feature engineering.

The leakage tests are the important ones. A volatility model that peeks
at the future scores beautifully offline and is worthless live, and
nothing about the metrics reveals it — only a test like
`test_feature_row_unchanged_when_future_is_removed` does.
"""

import numpy as np
import pandas as pd
import pytest

from app.ml.config import HORIZON_DAYS, TARGET_COLUMN, TRADING_DAYS_PER_YEAR
from app.ml.features import (
    FEATURE_NAMES,
    MAX_LOOKBACK,
    build_features,
    build_target,
    build_training_table,
    chronological_split,
    latest_feature_row,
)


class TestFeatureMatrix:

    def test_returns_exactly_the_declared_features_in_order(self, ohlcv, index_ohlcv):
        features = build_features(ohlcv, index_ohlcv)
        assert list(features.columns) == FEATURE_NAMES

    def test_index_is_preserved(self, ohlcv, index_ohlcv):
        features = build_features(ohlcv, index_ohlcv)
        pd.testing.assert_index_equal(features.index, ohlcv.index)

    def test_later_rows_are_fully_populated(self, ohlcv, index_ohlcv):
        features = build_features(ohlcv, index_ohlcv)
        assert not features.iloc[MAX_LOOKBACK:].isna().any().any()

    def test_no_infinities(self, ohlcv, index_ohlcv):
        features = build_features(ohlcv, index_ohlcv)
        assert not np.isinf(features.to_numpy(dtype=float)).any()

    def test_missing_index_leaves_index_features_na_only(self, ohlcv):
        features = build_features(ohlcv, None)

        assert features['idx_rv_21'].isna().all()
        assert features['idx_mom_21'].isna().all()
        # Everything else still computes
        others = [c for c in FEATURE_NAMES if not c.startswith('idx_')]
        assert not features[others].iloc[MAX_LOOKBACK:].isna().any().any()

    def test_rejects_frame_missing_columns(self, ohlcv):
        with pytest.raises(ValueError, match="missing columns"):
            build_features(ohlcv.drop(columns=['high']))

    def test_drawdown_is_never_positive(self, ohlcv, index_ohlcv):
        """Measured against a trailing maximum, so it cannot exceed zero."""
        dd = build_features(ohlcv, index_ohlcv)['drawdown_52w'].dropna()
        assert (dd <= 1e-12).all()

    def test_rsi_stays_within_bounds(self, ohlcv, index_ohlcv):
        rsi = build_features(ohlcv, index_ohlcv)['rsi_14'].dropna()
        assert rsi.between(0, 100).all()

    def test_volatility_features_are_positive(self, ohlcv, index_ohlcv):
        features = build_features(ohlcv, index_ohlcv)
        for col in ['rv_5', 'rv_10', 'rv_21', 'rv_63', 'parkinson_21', 'garman_klass_21']:
            assert (features[col].dropna() >= 0).all(), col

    def test_realised_vol_recovers_the_generating_volatility(self, index_ohlcv):
        """
        Sanity check on the estimator itself: fixtures are generated at a
        known annual volatility, so rv_21 should land near it on average.
        """
        from tests.conftest import make_ohlcv

        px = make_ohlcv(n_days=1500, seed=5, annual_vol=0.30)
        rv = build_features(px, index_ohlcv)['rv_21'].dropna()
        assert rv.mean() == pytest.approx(0.30, abs=0.05)


class TestTargetHasNoLookahead:

    def test_target_equals_forward_realised_volatility(self, ohlcv):
        """
        The target on row t must be the realised volatility of days
        t+1 .. t+HORIZON, computed independently here.
        """
        target = build_target(ohlcv)
        log_ret = np.log(ohlcv['close'] / ohlcv['close'].shift(1))

        for i in [300, 500, 700]:
            manual = (log_ret.iloc[i + 1: i + 1 + HORIZON_DAYS].std()
                      * np.sqrt(TRADING_DAYS_PER_YEAR))
            assert target.iloc[i] == pytest.approx(manual, rel=1e-9)

    def test_final_rows_are_na_because_the_future_is_unknown(self, ohlcv):
        target = build_target(ohlcv)
        assert target.tail(HORIZON_DAYS).isna().all()

    def test_target_is_not_merely_the_trailing_window(self, ohlcv):
        """Guards against an off-by-shift that would make the target backward-looking."""
        target = build_target(ohlcv)
        trailing = build_features(ohlcv, None)['rv_21']

        both = pd.concat([target, trailing], axis=1).dropna()
        assert not np.allclose(both.iloc[:, 0], both.iloc[:, 1])


class TestFeaturesHaveNoLookahead:

    def test_feature_row_unchanged_when_future_is_removed(self, ohlcv, index_ohlcv):
        """
        The decisive leakage test. Row t computed on the full series must
        equal row t computed on a series truncated at t. Any feature that
        peeks forward — a centred window, a reversed fill, a full-sample
        normalisation — breaks this.
        """
        full = build_features(ohlcv, index_ohlcv)

        for i in [400, 600, 800]:
            truncated = build_features(ohlcv.iloc[:i + 1], index_ohlcv)
            np.testing.assert_allclose(
                full.iloc[i].to_numpy(dtype=float),
                truncated.iloc[i].to_numpy(dtype=float),
                equal_nan=True,
                rtol=1e-12,
            )

    def test_index_features_do_not_pull_future_index_values(self, ohlcv, index_ohlcv):
        """
        Index data is reindexed onto the instrument's calendar with ffill.
        Forward-fill only carries earlier values forward, so truncating
        the index series must not change earlier rows.
        """
        i = 500
        full = build_features(ohlcv, index_ohlcv)
        truncated = build_features(ohlcv, index_ohlcv.iloc[:i + 1])

        np.testing.assert_allclose(
            full['idx_rv_21'].iloc[:i + 1].to_numpy(dtype=float),
            truncated['idx_rv_21'].iloc[:i + 1].to_numpy(dtype=float),
            equal_nan=True, rtol=1e-12,
        )


class TestTrainingTable:

    def test_contains_features_and_target_with_no_gaps(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)

        for name in FEATURE_NAMES:
            assert name in table.columns
        assert TARGET_COLUMN in table.columns
        assert not table.isna().any().any()

    def test_ticker_column_added_when_requested(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv, ticker='TEST.NS')
        assert (table['ticker'] == 'TEST.NS').all()

    def test_tables_from_several_instruments_concatenate(self, index_ohlcv):
        from tests.conftest import make_ohlcv

        panel = pd.concat([
            build_training_table(make_ohlcv(seed=s), index_ohlcv, ticker=f'T{s}')
            for s in [1, 2, 3]
        ])
        assert set(panel['ticker']) == {'T1', 'T2', 'T3'}
        assert not panel.isna().any().any()


class TestChronologicalSplit:

    def test_train_strictly_precedes_test(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        train, test = chronological_split(table)

        assert train.index.max() < test.index.min()

    def test_embargo_gap_is_applied(self, ohlcv, index_ohlcv):
        """
        Overlapping targets mean the last training row's target is built
        from returns reaching into the test period. The embargo must drop
        at least HORIZON_DAYS of trading dates between the halves.
        """
        table = build_training_table(ohlcv, index_ohlcv).sort_index()
        train, test = chronological_split(table, test_fraction=0.2)

        all_dates = table.index.unique().sort_values()
        embargoed = [
            d for d in all_dates
            if train.index.max() < d < test.index.min()
        ]
        assert len(embargoed) >= HORIZON_DAYS

    def test_embargo_counts_dates_not_rows_on_a_panel(self, index_ohlcv):
        """
        Regression test for a leak that a single-ticker test cannot see.

        On a multi-ticker panel there are N rows per date. An embargo
        measured in ROWS therefore collapses to roughly embargo/N trading
        days — for a 10-name panel, a 21-row embargo left just ONE day of
        separation, so the last training targets still overlapped the
        first ~20 test dates. The embargo must be counted in dates.
        """
        from tests.conftest import make_ohlcv

        panel = pd.concat([
            build_training_table(make_ohlcv(seed=s), index_ohlcv, ticker=f'T{s}')
            for s in range(10)
        ]).sort_index()

        rows_per_date = len(panel) / panel.index.nunique()
        assert rows_per_date == pytest.approx(10.0, abs=0.5)

        train, test = chronological_split(panel, test_fraction=0.2)

        embargoed = [
            d for d in panel.index.unique().sort_values()
            if train.index.max() < d < test.index.min()
        ]
        assert len(embargoed) >= HORIZON_DAYS, (
            f"only {len(embargoed)} trading dates embargoed on a "
            f"{rows_per_date:.0f}-rows-per-date panel"
        )

    def test_panel_split_keeps_every_ticker_in_both_halves(self, index_ohlcv):
        """A chronological split must not drop whole tickers."""
        from tests.conftest import make_ohlcv

        panel = pd.concat([
            build_training_table(make_ohlcv(seed=s), index_ohlcv, ticker=f'T{s}')
            for s in range(5)
        ]).sort_index()

        train, test = chronological_split(panel, test_fraction=0.2)

        assert set(train['ticker']) == set(panel['ticker'])
        assert set(test['ticker']) == set(panel['ticker'])

    def test_no_row_appears_in_both_halves(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv)
        train, test = chronological_split(table)

        assert not set(train.index) & set(test.index)

    @pytest.mark.parametrize("fraction", [0.0, 1.0, -0.1, 1.5])
    def test_invalid_fraction_rejected(self, ohlcv, index_ohlcv, fraction):
        table = build_training_table(ohlcv, index_ohlcv)
        with pytest.raises(ValueError):
            chronological_split(table, test_fraction=fraction)

    def test_too_few_rows_rejected(self, ohlcv, index_ohlcv):
        table = build_training_table(ohlcv, index_ohlcv).head(20)
        with pytest.raises(ValueError, match="Not enough rows"):
            chronological_split(table, test_fraction=0.2)


class TestLatestFeatureRow:

    def test_returns_one_row_in_declared_order(self, ohlcv, index_ohlcv):
        row, as_of = latest_feature_row(ohlcv, index_ohlcv)

        assert len(row) == 1
        assert list(row.columns) == FEATURE_NAMES
        assert not row.isna().any().any()
        assert as_of in ohlcv.index

    def test_raises_when_history_is_too_short(self, short_ohlcv, index_ohlcv):
        with pytest.raises(ValueError, match="No complete feature row"):
            latest_feature_row(short_ohlcv, index_ohlcv)
