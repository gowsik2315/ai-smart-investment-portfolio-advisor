"""
Tests for scripts/train_volatility_model.py.

The script decides whether a model is saved, so the logic that guards that
decision is tested like any other calculation. The cases that matter most:

* the embargo is measured in distinct trading DATES. On a pooled panel a
  row-based embargo leaves a gap of one or two dates, not 21, and the
  overlapping targets leak; the script must notice and re-split;
* walk-forward folds are built by date and never overlap;
* a model is accepted only if it beats naive persistence on BOTH RMSE and
  QLIKE;
* nothing the script puts in a pipeline can be an object defined in the
  script (the backend must unpickle it), and predictions cannot go negative.

Everything runs offline on synthetic prices.
"""

import ast
import importlib.util
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.ml.config import EMBARGO_DAYS, TARGET_COLUMN
from app.ml.features import FEATURE_NAMES, build_training_table
from tests.conftest import make_ohlcv

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "train_volatility_model.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("train_volatility_model", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tvm = _load_script()


@pytest.fixture(scope="module")
def panel():
    """Six tickers stacked on shared dates, exactly like the real pooled panel."""
    index = make_ohlcv(seed=99, annual_vol=0.16, annual_drift=0.09)
    frames = [
        build_training_table(make_ohlcv(seed=s, annual_vol=0.18 + 0.03 * s), index, ticker=f"T{s}")
        for s in range(1, 7)
    ]
    pooled = pd.concat(frames)
    pooled.index.name = "date"
    pooled = pooled[FEATURE_NAMES + [TARGET_COLUMN, "ticker"]]
    return pooled.reset_index().sort_values(["date", "ticker"], kind="stable").set_index("date")


def row_based_split(table, test_fraction=0.2, embargo=EMBARGO_DAYS):
    """The faulty splitter: drops `embargo` ROWS, which is ~embargo/6 dates here."""
    ordered = table.sort_index()
    cut = len(ordered) - int(len(ordered) * test_fraction)
    return ordered.iloc[: cut - embargo], ordered.iloc[cut:]


# ── Source constraints ───────────────────────────────────────────────

class TestSourceConstraints:

    def test_script_defines_no_lambdas_and_no_classes(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        assert not [n for n in ast.walk(tree) if isinstance(n, ast.Lambda)]
        assert not [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

    def test_ridge_grid_extends_past_the_original_edge(self):
        """The optimum was clipped at 10000 by the first grid."""
        assert tvm.RIDGE_ALPHAS[:6] == [1, 10, 100, 1000, 3000, 10000]
        assert max(tvm.RIDGE_ALPHAS) >= 300000


# ── The embargo, measured in dates ───────────────────────────────────

class TestDateGap:

    def test_counts_distinct_dates_strictly_between(self):
        dates = pd.bdate_range("2024-01-01", periods=10)
        assert tvm.date_gap(dates, dates[0], dates[5]) == 4
        assert tvm.date_gap(dates, dates[2], dates[3]) == 0

    def test_unknown_date_is_an_error(self):
        dates = pd.bdate_range("2024-01-01", periods=10)
        with pytest.raises(ValueError):
            tvm.date_gap(dates, dates[0], pd.Timestamp("1999-01-01"))


class TestEmbargoVerification:

    def test_the_library_split_embargoes_by_dates_on_a_pooled_panel(self, panel):
        train, test = tvm.chronological_split(panel, test_fraction=0.2)
        dates = panel.index.unique().sort_values()

        assert tvm.date_gap(dates, train.index.max(), test.index.min()) >= EMBARGO_DAYS

    def test_split_by_date_leaves_the_full_embargo(self, panel):
        train, test = tvm.split_by_date(panel, 0.2, EMBARGO_DAYS)
        dates = panel.index.unique().sort_values()

        assert tvm.date_gap(dates, train.index.max(), test.index.min()) == EMBARGO_DAYS
        assert train.index.max() < test.index.min()

    def test_a_row_based_embargo_really_does_leak_on_a_pooled_panel(self, panel):
        """Establishes that the failure the script guards against is real."""
        train, test = row_based_split(panel)
        dates = panel.index.unique().sort_values()

        assert tvm.date_gap(dates, train.index.max(), test.index.min()) < EMBARGO_DAYS

    def test_script_detects_a_row_based_split_and_repairs_it(self, panel, monkeypatch, capsys):
        monkeypatch.setattr(tvm, "chronological_split", row_based_split)

        train, test, gap = tvm.split_panel(panel, 0.2)
        out = capsys.readouterr().out

        assert "GAP TOO SMALL" in out and "Re-splitting by date" in out
        assert gap >= EMBARGO_DAYS
        dates = panel.index.unique().sort_values()
        assert tvm.date_gap(dates, train.index.max(), test.index.min()) >= EMBARGO_DAYS

    def test_a_correct_split_is_left_alone(self, panel, capsys):
        tvm.split_panel(panel, 0.2)
        out = capsys.readouterr().out

        assert "GAP TOO SMALL" not in out
        assert "no re-split needed" in out


# ── Walk-forward folds ───────────────────────────────────────────────

class TestDateFolds:

    @pytest.fixture(scope="class")
    def folds(self, panel):
        train, _ = tvm.split_by_date(panel, 0.2, EMBARGO_DAYS)
        return tvm.date_folds(train, 5, EMBARGO_DAYS)

    def test_every_fold_keeps_the_embargo(self, folds):
        assert len(folds) == 5
        assert all(f["gap"] >= EMBARGO_DAYS for f in folds)

    def test_train_always_precedes_validation_with_no_shared_dates(self, folds):
        for f in folds:
            assert f["train"].index.max() < f["val"].index.min()
            assert not set(f["train"].index.unique()) & set(f["val"].index.unique())

    def test_no_ticker_is_split_across_the_boundary_of_a_single_date(self, folds):
        """A row-based fold would put some tickers of one date in train and the rest in validation."""
        for f in folds:
            boundary = f["val"].index.min()
            assert (f["train"].index < boundary).all()

    def test_training_window_expands(self, folds):
        sizes = [len(f["train"]) for f in folds]
        assert sizes == sorted(sizes) and len(set(sizes)) == len(sizes)

    def test_too_many_folds_aborts_instead_of_silently_shrinking(self, panel):
        train, _ = tvm.split_by_date(panel, 0.2, EMBARGO_DAYS)
        with pytest.raises(SystemExit):
            tvm.date_folds(train, 60, EMBARGO_DAYS)


# ── Selection: one standard error rule ───────────────────────────────

def entry(mean, std):
    return {"qlike_mean": mean, "qlike_std": std}


class TestSelectFamily:

    def test_prefers_the_simplest_family_within_one_standard_error(self):
        best = {"ridge": entry(0.1863, 0.0405), "hist_gb": entry(0.1907, 0.0517),
                "random_forest": entry(0.1842, 0.0490)}
        chosen, lowest, se, threshold, within = tvm.select_family(best, 5)

        assert lowest == "random_forest"
        assert chosen == "ridge"
        assert within == ["ridge", "hist_gb", "random_forest"]
        assert se == pytest.approx(0.0490 / 2.0)
        assert threshold == pytest.approx(0.1842 + se)

    def test_takes_the_best_family_when_a_simpler_one_is_clearly_worse(self):
        best = {"ridge": entry(0.30, 0.02), "hist_gb": entry(0.25, 0.02),
                "random_forest": entry(0.18, 0.02)}
        chosen, lowest, _, _, within = tvm.select_family(best, 5)

        assert chosen == lowest == "random_forest"
        assert within == ["random_forest"]

    def test_between_two_nonlinear_families_the_simpler_wins_a_tie(self):
        best = {"ridge": entry(0.40, 0.02), "hist_gb": entry(0.1907, 0.05),
                "random_forest": entry(0.1842, 0.05)}
        assert tvm.select_family(best, 5)[0] == "hist_gb"


# ── Acceptance ───────────────────────────────────────────────────────

def comparison(model_rmse, model_qlike, naive_rmse=0.0823, naive_qlike=0.3638):
    return pd.DataFrame({
        "rmse": [model_rmse, naive_rmse], "mae": [0.05, 0.06],
        "qlike": [model_qlike, naive_qlike], "r2": [0.2, -0.2],
        "rmse_vs_baseline": [(1 - model_rmse / naive_rmse) * 100, 0.0],
        "qlike_vs_baseline": [(1 - model_qlike / naive_qlike) * 100, 0.0],
    }, index=["model", "naive_persistence"])


class TestAcceptance:

    def test_accepts_when_both_metrics_beat_naive(self):
        accepted, reasons = tvm.acceptance(comparison(0.07, 0.20))
        assert accepted and reasons == []

    @pytest.mark.parametrize("rmse, qlike, expected", [
        (0.09, 0.20, ["does not beat naive persistence on RMSE"]),
        (0.07, 0.40, ["does not beat naive persistence on QLIKE"]),
        (0.09, 0.40, ["does not beat naive persistence on RMSE",
                      "does not beat naive persistence on QLIKE"]),
    ])
    def test_rejects_when_either_metric_fails(self, rmse, qlike, expected):
        accepted, reasons = tvm.acceptance(comparison(rmse, qlike))
        assert not accepted and reasons == expected

    def test_a_tie_is_not_a_win(self):
        accepted, _ = tvm.acceptance(comparison(0.0823, 0.3638))
        assert not accepted


# ── Environment check ────────────────────────────────────────────────

class TestParseRequirements:

    def test_reads_pins_and_ignores_comments_and_unpinned_lines(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text(
            "# comment\nscikit-learn==1.9.0  # inline\nNumPy==2.5.2\n"
            "Some_Package==1.0\nunpinned-package\nrequests>=2\n",
            encoding="utf-8",
        )
        pins = tvm.parse_requirements(req)

        assert pins == {"scikit-learn": "1.9.0", "numpy": "2.5.2", "some-package": "1.0"}

    def test_the_real_requirements_file_pins_what_the_script_compares(self):
        pins = tvm.parse_requirements(tvm.BACKEND_DIR / "requirements.txt")
        for name in ("scikit-learn", "numpy", "pandas", "joblib"):
            assert name in pins


# ── The estimators themselves ────────────────────────────────────────

FACTORIES = {
    "ridge": lambda: tvm.make_ridge(1000),
    "hist_gb": lambda: tvm.make_hist_gb(2, 50),
    "random_forest": lambda: tvm.make_random_forest(3, 50),
}


@pytest.fixture(scope="module")
def fitted(panel):
    X, y = panel[FEATURE_NAMES], panel[TARGET_COLUMN]
    return {name: make().fit(X, y) for name, make in FACTORIES.items()}


@pytest.mark.parametrize("family", list(FACTORIES))
class TestEstimators:

    def test_predictions_are_positive_and_finite(self, family, fitted, panel):
        pred = fitted[family].predict(panel[FEATURE_NAMES])
        assert np.isfinite(pred).all() and (pred > 0).all()

    def test_predictions_cannot_go_negative_even_for_absurd_inputs(self, family, fitted, panel):
        """
        The point of fitting log(volatility) and inverting with exp. Note what
        is NOT promised: with inputs this wild a linear model's log prediction
        can overflow exp() to +inf. That is still positive; the serving guard
        (test below) is what rejects it.
        """
        pred = fitted[family].predict(panel[FEATURE_NAMES] * 1000.0)
        assert not np.isnan(pred).any()
        assert (pred > 0).all()

    def test_predictions_stay_finite_for_merely_unusual_inputs(self, family, fitted, panel):
        pred = fitted[family].predict(panel[FEATURE_NAMES] * 10.0)
        assert np.isfinite(pred).all() and (pred > 0).all()

    def test_an_overflowed_prediction_is_rejected_by_the_serving_guard(self, family, fitted, panel):
        """If a bad data day makes the model emit inf, the service must not pass it on."""
        from app.ml.model_registry import VolatilityModelArtifact
        from app.services.ml_prediction_service import SOURCE_HISTORICAL, VolatilityPredictionService

        class Overflowing:
            def predict(self, X):
                return fitted[family].predict(X * 1000.0)

        service = VolatilityPredictionService()
        service._load_attempted = True
        service._artifact = VolatilityModelArtifact(
            model=Overflowing(), feature_names=FEATURE_NAMES, model_version="overflow")

        ohlcv, index = make_ohlcv(), make_ohlcv(seed=99)
        historical = service._historical_volatility(ohlcv)
        forecast = service._try_ml_forecast("TEST.NS", ohlcv, index, historical)

        raw = fitted[family].predict(panel[FEATURE_NAMES].tail(1) * 1000.0)[0]
        if 0.01 <= raw <= 3.0:
            pytest.skip(f"{family} stays inside the plausible range even for absurd inputs")

        assert forecast.source == SOURCE_HISTORICAL
        assert forecast.volatility == historical

    def test_target_transform_is_numpy_log_and_exp(self, family, fitted):
        assert fitted[family].func is np.log
        assert fitted[family].inverse_func is np.exp

    def test_pickle_has_no_reference_to_the_script(self, family, fitted):
        blob = pickle.dumps(fitted[family])
        assert b"__main__" not in blob
        assert b"train_volatility_model" not in blob

    def test_script_guard_accepts_a_clean_estimator(self, family, fitted):
        tvm.assert_unpicklable_references_absent(fitted[family])

    def test_round_trips_through_pickle_with_identical_predictions(self, family, fitted, panel):
        X = panel[FEATURE_NAMES].head(50)
        clone = pickle.loads(pickle.dumps(fitted[family]))
        np.testing.assert_allclose(clone.predict(X), fitted[family].predict(X))


class TestPickleGuard:

    def test_a_reference_to_main_is_caught(self):
        from sklearn.linear_model import LinearRegression

        def helper(x):
            return x
        helper.__module__ = "__main__"
        model = LinearRegression()
        model.helper = helper

        with pytest.raises((AssertionError, pickle.PicklingError, AttributeError)):
            tvm.assert_unpicklable_references_absent(model)

    def test_only_the_wrapped_regressor_differs_between_families(self):
        for make in FACTORIES.values():
            est = make()
            assert type(est).__name__ == "TransformedTargetRegressor"
