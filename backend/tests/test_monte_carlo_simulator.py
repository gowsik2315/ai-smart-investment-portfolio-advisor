"""
Tests for the Monte Carlo simulator.

The simulator was changed from an additive random walk to geometric
Brownian motion so that a model-predicted volatility — which can be much
larger than a hand-typed one — cannot drive paths negative. These tests
pin that behaviour down.
"""

import numpy as np
import pytest

from app.services.monte_carlo_simulator import MonteCarloSimulator, PERIODS_PER_YEAR


class TestDeterministicBehaviour:

    def test_zero_volatility_matches_exact_compounding(self):
        """With no volatility, the result must be plain compound growth."""
        result = MonteCarloSimulator.run_simulation(
            initial_investment=100_000, expected_return=0.12, volatility=0.0,
            years=10, num_simulations=1000, random_seed=42,
        )
        expected = 100_000 * 1.12 ** 10

        # Reported statistics are rounded to 2dp, so compare at that scale
        assert result['statistics']['mean_value'] == pytest.approx(expected, abs=0.01)
        assert result['statistics']['std_deviation'] == pytest.approx(0.0, abs=1e-6)

    def test_same_seed_gives_identical_results(self):
        a = MonteCarloSimulator.run_simulation(
            100_000, 0.10, 0.20, 5, 2000, random_seed=99)
        b = MonteCarloSimulator.run_simulation(
            100_000, 0.10, 0.20, 5, 2000, random_seed=99)

        assert a['statistics'] == b['statistics']
        np.testing.assert_array_equal(a['final_values'], b['final_values'])

    def test_different_seeds_give_different_results(self):
        a = MonteCarloSimulator.run_simulation(100_000, 0.10, 0.20, 5, 2000, random_seed=1)
        b = MonteCarloSimulator.run_simulation(100_000, 0.10, 0.20, 5, 2000, random_seed=2)

        assert a['statistics']['mean_value'] != b['statistics']['mean_value']


class TestGeometricProperties:

    @pytest.mark.parametrize("volatility", [0.15, 0.50, 1.20, 2.00])
    def test_paths_never_go_negative(self, volatility):
        """
        The whole point of the geometric formulation. The previous
        additive model could produce a draw below -100% in a single
        month, which zeroed or inverted the path permanently.
        """
        result = MonteCarloSimulator.run_simulation(
            initial_investment=100_000, expected_return=0.12,
            volatility=volatility, years=30, num_simulations=5000,
            monthly_contribution=5000, random_seed=3,
        )
        assert result['final_values'].min() > 0

    @pytest.mark.parametrize("volatility", [0.15, 0.50, 1.20])
    def test_drift_is_preserved_in_log_space(self, volatility):
        """
        The Ito correction must hold the expected return at the requested
        level. Checked in log space because the arithmetic sample mean of
        a lognormal is a very high-variance estimator — at high sigma it
        deviates from the true mean by tens of percent even with 50k
        paths, which would make an arithmetic assertion flaky and
        meaningless.

            E[ln(S_T / S_0)] = years*ln(1+mu) - 0.5*sigma^2*years
        """
        years, mu = 10, 0.12
        result = MonteCarloSimulator.run_simulation(
            initial_investment=100_000, expected_return=mu,
            volatility=volatility, years=years, num_simulations=50_000,
            monthly_contribution=0.0, random_seed=7,
        )

        empirical = np.mean(np.log(result['final_values'] / 100_000))
        theoretical = years * np.log1p(mu) - 0.5 * volatility ** 2 * years

        assert empirical == pytest.approx(theoretical, abs=0.02)

    def test_higher_volatility_widens_the_distribution(self):
        low = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.10, 10, 20_000, random_seed=5)
        high = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.40, 10, 20_000, random_seed=5)

        low_ci = low['confidence_intervals']['ci_95']
        high_ci = high['confidence_intervals']['ci_95']

        assert (high_ci['upper'] - high_ci['lower']) > (low_ci['upper'] - low_ci['lower'])

    def test_contributions_increase_total_and_outcome(self):
        without = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.15, 10, 5000, monthly_contribution=0, random_seed=11)
        with_contrib = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.15, 10, 5000, monthly_contribution=5000, random_seed=11)

        expected_total = 100_000 + 5000 * 10 * PERIODS_PER_YEAR
        assert with_contrib['statistics']['total_contributions'] == pytest.approx(expected_total)
        assert (with_contrib['scenarios']['average_case']
                > without['scenarios']['average_case'])


class TestRiskMetrics:
    """
    These were previously computed by the service but never populated in
    the API response — the route had no access to the terminal values.
    """

    def test_risk_metrics_are_present(self):
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.20, 10, 5000, random_seed=13)

        assert 'risk_metrics' in result
        for key in ['var_5_percent', 'var_loss_amount', 'var_loss_percent',
                    'cvar_5_percent', 'cvar_loss_amount', 'cvar_loss_percent']:
            assert key in result['risk_metrics']

    def test_cvar_is_never_above_var(self):
        """CVaR averages the tail below VaR, so it cannot exceed it."""
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.35, 15, 10_000, monthly_contribution=2000, random_seed=17)
        rm = result['risk_metrics']

        assert rm['cvar_5_percent'] <= rm['var_5_percent']
        assert rm['cvar_loss_amount'] >= rm['var_loss_amount']

    def test_var_equals_fifth_percentile_of_terminal_values(self):
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.25, 10, 10_000, random_seed=19)

        expected = np.percentile(result['final_values'], 5)
        assert result['risk_metrics']['var_5_percent'] == pytest.approx(expected, rel=1e-6)


class TestStatisticsConsistency:

    def test_probabilities_sum_to_one_hundred(self):
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.20, 10, 10_000, random_seed=23)
        stats = result['statistics']

        assert (stats['probability_of_profit'] + stats['probability_of_loss']
                == pytest.approx(100.0, abs=0.01))

    def test_scenarios_are_ordered(self):
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.20, 10, 10_000, random_seed=29)
        s = result['scenarios']

        assert s['worst_case'] < s['average_case'] < s['best_case']

    def test_confidence_intervals_nest(self):
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.20, 10, 10_000, random_seed=31)
        ci = result['confidence_intervals']

        assert ci['ci_99']['lower'] <= ci['ci_95']['lower'] <= ci['ci_90']['lower']
        assert ci['ci_99']['upper'] >= ci['ci_95']['upper'] >= ci['ci_90']['upper']

    def test_percentile_paths_are_ordered_at_every_step(self):
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.20, 5, 5000, random_seed=37)
        p = result['percentile_paths']

        for i in range(len(p['p50'])):
            assert p['p10'][i] <= p['p25'][i] <= p['p50'][i] <= p['p75'][i] <= p['p90'][i]

    def test_path_arrays_have_one_entry_per_period_boundary(self):
        years = 7
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 0.20, years, 2000, random_seed=41)

        expected_len = years * PERIODS_PER_YEAR + 1
        assert len(result['time_periods']) == expected_len
        assert len(result['percentile_paths']['p50']) == expected_len


class TestValidation:

    @pytest.mark.parametrize("kwargs, message", [
        (dict(initial_investment=0), "Initial investment"),
        (dict(initial_investment=-100), "Initial investment"),
        (dict(years=0), "Years must be"),
        (dict(years=51), "Years must be"),
        (dict(num_simulations=999), "Number of simulations"),
        (dict(num_simulations=50_001), "Number of simulations"),
        (dict(volatility=-0.1), "Volatility cannot be negative"),
        (dict(expected_return=-1.0), "Expected return must be greater"),
        (dict(monthly_contribution=-500), "Monthly contribution cannot be negative"),
    ])
    def test_invalid_inputs_are_rejected(self, kwargs, message):
        base = dict(
            initial_investment=100_000, expected_return=0.12, volatility=0.15,
            years=10, num_simulations=10_000, monthly_contribution=0.0,
        )
        base.update(kwargs)

        with pytest.raises(ValueError, match=message):
            MonteCarloSimulator.run_simulation(**base)

    def test_volatility_above_one_is_accepted(self):
        """
        A predicted volatility can exceed 100% annualised. The simulator
        must handle it rather than treating 1.0 as a ceiling.
        """
        result = MonteCarloSimulator.run_simulation(
            100_000, 0.12, 1.75, 10, 2000, random_seed=43)

        assert result['volatility'] == 1.75
        assert result['final_values'].min() > 0
