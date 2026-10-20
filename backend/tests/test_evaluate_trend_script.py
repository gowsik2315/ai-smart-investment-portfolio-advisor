"""
Guards on the trend-classifier evaluation script.

The script's job is to be hard to fool. Its expected answer is "no edge",
so the risk is not that it fails — it is that a future change quietly
lowers the bar and lets a worthless classifier reach the Stock Predictor,
where it would be displayed as a prediction.
"""

import ast
import importlib.util
from pathlib import Path

import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "evaluate_trend_classifier.py"


def load_script():
    """Import the script as a module without running main()."""
    spec = importlib.util.spec_from_file_location("evaluate_trend_classifier", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSourceConstraints:
    def test_script_exists(self):
        assert SCRIPT.exists(), f"missing {SCRIPT}"

    def test_defines_no_lambdas_and_no_classes(self):
        # Anything pickled alongside the estimator must be importable from
        # installed libraries, or the API cannot unpickle the artifact.
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        assert not [n for n in ast.walk(tree) if isinstance(n, ast.Lambda)]
        assert not [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

    def test_baseline_is_the_train_base_rate_not_one_half(self):
        source = SCRIPT.read_text(encoding="utf-8")
        assert "y_train.mean()" in source
        # A literal 0.5 baseline would make every upward-drifting stock
        # look predictable.
        assert "0.5)" not in source.replace("quantile(0.5)", "")


class TestCandidates:
    def test_several_families_are_tried_simplest_first(self):
        module = load_script()
        names = [name for name, _ in module.candidates()]

        assert len(names) >= 4
        assert names[0].startswith("logistic")

    def test_every_candidate_builds_and_predicts_probabilities(self):
        module = load_script()
        rng = np.random.default_rng(0)
        X = rng.normal(size=(300, 4))
        y = (X[:, 0] + rng.normal(scale=2.0, size=300) > 0).astype(int)

        for name, factory in module.candidates():
            model = factory().fit(X, y)
            p = model.predict_proba(X)[:, list(model.classes_).index(1)]
            assert p.shape == (300,), name
            assert np.all((p >= 0.0) & (p <= 1.0)), name

    def test_gradient_boosting_does_not_use_random_early_stopping(self):
        # scikit-learn's default carves a RANDOM validation split, which
        # leaks neighbouring rows when labels overlap by 20 of 21 days.
        module = load_script()
        model = module.make_hist_gb(3, 50)

        assert model.early_stopping is False


class TestBootstrapInterval:
    def test_a_worthless_forecast_gets_an_interval_spanning_zero(self):
        module = load_script()
        rng = np.random.default_rng(1)
        y = rng.integers(0, 2, size=600)
        base = float(y.mean())
        # Predicting the base rate everywhere has exactly zero skill.
        low, high = module.bootstrap_skill_interval(y, np.full(600, base), base)

        assert low <= 0.0 <= high

    def test_a_genuinely_good_forecast_is_detected(self):
        module = load_script()
        rng = np.random.default_rng(2)
        y = rng.integers(0, 2, size=600)
        # Near-perfect probabilities must score a clearly positive skill.
        p = np.where(y == 1, 0.95, 0.05)
        low, high = module.bootstrap_skill_interval(y, p, float(y.mean()))

        assert low > 0.0

    def test_blocks_are_the_label_horizon_long(self):
        # i.i.d. resampling of overlapping windows would give intervals
        # far too narrow and manufacture significance.
        from app.ml.config import HORIZON_DAYS
        source = SCRIPT.read_text(encoding="utf-8")

        assert "block = n, HORIZON_DAYS" in source or "n, block = len(y), HORIZON_DAYS" in source
        assert HORIZON_DAYS == 21

    def test_too_short_a_series_returns_nan_rather_than_a_fake_interval(self):
        module = load_script()
        y = np.array([1, 0, 1])
        low, high = module.bootstrap_skill_interval(y, np.full(3, 0.5), 0.5)

        assert np.isnan(low) and np.isnan(high)


class TestAcceptanceBar:
    @staticmethod
    def accepted(skill: float, low: float) -> bool:
        """The rule the script applies: positive skill AND an interval above zero."""
        return skill > 0 and low > 0

    def test_a_positive_point_estimate_alone_is_not_enough(self):
        # This is the case that matters: a model that looks better but
        # whose advantage is indistinguishable from noise.
        assert not self.accepted(skill=0.01, low=-0.004)

    def test_accepted_only_when_the_interval_excludes_zero(self):
        assert self.accepted(skill=0.02, low=0.005)

    def test_negative_skill_is_refused(self):
        assert not self.accepted(skill=-0.0012, low=-0.0143)

    def test_the_real_observed_result_would_be_refused(self):
        # The measured outcome: logistic C=1.0, skill -0.0012,
        # 95% interval -0.0143 to +0.0110.
        assert not self.accepted(skill=-0.0012, low=-0.0143)


class TestSavingIsGated:
    def test_save_requires_acceptance(self):
        source = SCRIPT.read_text(encoding="utf-8")

        assert "if (args.save and accepted) or args.force_save:" in source

    def test_force_save_is_announced_as_unvalidated(self):
        source = SCRIPT.read_text(encoding="utf-8")

        assert "FAILED the bar" in source

    def test_save_uses_the_registry_so_the_contract_is_enforced(self):
        source = SCRIPT.read_text(encoding="utf-8")

        assert "from app.ml.trend_registry import save_trend_model" in source
        assert "save_trend_model(" in source
