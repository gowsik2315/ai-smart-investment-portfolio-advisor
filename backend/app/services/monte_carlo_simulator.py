"""
Monte Carlo Portfolio Simulation Service
Generates portfolio projections using geometric Brownian motion.

MODEL NOTE
----------
Monthly steps are drawn in LOG space and applied multiplicatively:

    S[t+1] = S[t] * exp(m_dt + s_dt * Z),   Z ~ N(0, 1)

with the Ito correction applied so that the simulated arithmetic
expectation matches the `expected_return` the caller asked for:

    dt   = 1/12
    s_dt = sigma * sqrt(dt)
    m_dt = dt * ln(1 + mu) - (s_dt ** 2) / 2

This replaced an earlier additive formulation, `S[t+1] = S[t] * (1 + r)`
with `r ~ N(mu/12, sigma/sqrt(12))`. That version could drive a portfolio
negative once sigma got large (a single draw below -100% wipes the path
out and the compounding never recovers), which matters a great deal here:
this simulator is about to be fed a *predicted* volatility that can be
far higher than the 15% a user types by hand. Log-space steps keep every
path strictly positive, which is also the standard assumption the
project documentation already claims is in use.
"""

import numpy as np
from typing import Dict, Optional

# Monthly stepping: 12 periods per year
PERIODS_PER_YEAR = 12


class MonteCarloSimulator:
    """
    Monte Carlo simulator for portfolio projections.

    Simulates portfolio value paths under geometric Brownian motion with
    optional level monthly contributions.
    """

    @staticmethod
    def run_simulation(
        initial_investment: float,
        expected_return: float,
        volatility: float,
        years: int,
        num_simulations: int = 10000,
        monthly_contribution: float = 0.0,
        random_seed: Optional[int] = None
    ) -> Dict:
        """
        Run a Monte Carlo simulation for a portfolio.

        Args:
            initial_investment: Starting portfolio value
            expected_return: Expected annual return (decimal, e.g. 0.12 = 12%)
            volatility: Annual volatility (decimal, e.g. 0.15 = 15%).
                May exceed 1.0 — a model-predicted volatility for a single
                equity can legitimately clear 100% annualised in a crisis.
            years: Investment duration in years
            num_simulations: Number of simulated paths (1,000-50,000)
            monthly_contribution: Level monthly contribution, added at the
                end of each month
            random_seed: Seed for reproducible output. Pass a fixed value
                when comparing two parameter sets (for example a predicted
                volatility against a manual one) so the difference you see
                is the parameter and not the draw.

        Returns:
            dict of statistics, scenarios, confidence intervals, risk
            metrics, percentile paths and histogram data. Also includes
            `final_values` (the raw terminal values) so callers can derive
            further metrics without re-running the simulation.
        """
        if initial_investment <= 0:
            raise ValueError("Initial investment must be greater than 0")

        if years <= 0 or years > 50:
            raise ValueError("Years must be between 1 and 50")

        if num_simulations < 1000 or num_simulations > 50000:
            raise ValueError("Number of simulations must be between 1000 and 50000")

        if volatility < 0:
            raise ValueError("Volatility cannot be negative")

        if expected_return <= -1:
            raise ValueError("Expected return must be greater than -100%")

        if monthly_contribution < 0:
            raise ValueError("Monthly contribution cannot be negative")

        rng = np.random.default_rng(random_seed)

        num_periods = years * PERIODS_PER_YEAR
        dt = 1.0 / PERIODS_PER_YEAR

        # Per-step log-return parameters, with the Ito correction so the
        # simulated arithmetic mean matches `expected_return`.
        step_sigma = volatility * np.sqrt(dt)
        step_drift = dt * np.log1p(expected_return) - 0.5 * (step_sigma ** 2)

        # Multiplicative growth factors for every path and period
        growth_factors = np.exp(
            rng.normal(step_drift, step_sigma, size=(num_simulations, num_periods))
        )

        portfolio_values = np.zeros((num_simulations, num_periods + 1))
        portfolio_values[:, 0] = initial_investment

        for period in range(num_periods):
            # Apply the month's return, then add that month's contribution
            grown = portfolio_values[:, period] * growth_factors[:, period]
            if monthly_contribution > 0:
                grown += monthly_contribution
            portfolio_values[:, period + 1] = grown

        final_values = portfolio_values[:, -1]

        statistics = MonteCarloSimulator._calculate_statistics(
            final_values=final_values,
            initial_investment=initial_investment,
            monthly_contribution=monthly_contribution,
            num_periods=num_periods
        )

        scenarios = MonteCarloSimulator._calculate_scenarios(final_values)
        confidence_intervals = MonteCarloSimulator._calculate_confidence_intervals(final_values)

        # Risk metrics are computed here rather than left to the caller.
        # Previously the route had no access to `final_values` and so the
        # VaR/CVaR fields were never populated at all.
        risk_metrics = MonteCarloSimulator.calculate_risk_metrics(
            final_values=final_values,
            total_contributions=statistics['total_contributions']
        )

        percentile_paths = {
            'p10': np.percentile(portfolio_values, 10, axis=0).tolist(),
            'p25': np.percentile(portfolio_values, 25, axis=0).tolist(),
            'p50': np.percentile(portfolio_values, 50, axis=0).tolist(),
            'p75': np.percentile(portfolio_values, 75, axis=0).tolist(),
            'p90': np.percentile(portfolio_values, 90, axis=0).tolist(),
        }

        histogram_data = MonteCarloSimulator._calculate_histogram(final_values)

        # Thin sample of individual paths for the chart's background lines
        sample_interval = max(1, num_simulations // 100)
        simulation_paths = [
            path.tolist() for path in portfolio_values[::sample_interval, :][:20]
        ]

        return {
            'statistics': statistics,
            'scenarios': scenarios,
            'confidence_intervals': confidence_intervals,
            'risk_metrics': risk_metrics,
            'simulation_paths': simulation_paths,
            'percentile_paths': percentile_paths,
            'time_periods': list(range(num_periods + 1)),
            'histogram_data': histogram_data,
            'num_simulations': num_simulations,
            'years': years,
            'initial_investment': initial_investment,
            'monthly_contribution': monthly_contribution,
            'expected_return': expected_return,
            'volatility': volatility,
            'final_values': final_values,
        }

    @staticmethod
    def _calculate_statistics(
        final_values: np.ndarray,
        initial_investment: float,
        monthly_contribution: float,
        num_periods: int
    ) -> Dict:
        """Summary statistics over the terminal portfolio values."""

        total_contributions = initial_investment + (monthly_contribution * num_periods)

        mean_value = float(np.mean(final_values))
        median_value = float(np.median(final_values))
        std_value = float(np.std(final_values))
        min_value = float(np.min(final_values))
        max_value = float(np.max(final_values))

        # Return measured against total money put in, not just the opening
        # balance — otherwise contributions read as investment gains.
        mean_return = ((mean_value - total_contributions) / total_contributions) * 100
        median_return = ((median_value - total_contributions) / total_contributions) * 100

        num_paths = len(final_values)
        probability_of_profit = float(np.sum(final_values > total_contributions) / num_paths) * 100
        probability_of_doubling = float(np.sum(final_values >= total_contributions * 2) / num_paths) * 100
        probability_of_loss = float(np.sum(final_values < total_contributions) / num_paths) * 100

        return {
            'mean_value': round(mean_value, 2),
            'median_value': round(median_value, 2),
            'std_deviation': round(std_value, 2),
            'min_value': round(min_value, 2),
            'max_value': round(max_value, 2),
            'mean_return_percent': round(mean_return, 2),
            'median_return_percent': round(median_return, 2),
            'probability_of_profit': round(probability_of_profit, 2),
            'probability_of_doubling': round(probability_of_doubling, 2),
            'probability_of_loss': round(probability_of_loss, 2),
            'total_contributions': round(total_contributions, 2)
        }

    @staticmethod
    def _calculate_scenarios(final_values: np.ndarray) -> Dict:
        """Best (p95), average (p50) and worst (p5) terminal outcomes."""
        return {
            'best_case': round(float(np.percentile(final_values, 95)), 2),
            'average_case': round(float(np.percentile(final_values, 50)), 2),
            'worst_case': round(float(np.percentile(final_values, 5)), 2)
        }

    @staticmethod
    def _calculate_confidence_intervals(final_values: np.ndarray) -> Dict:
        """Central 90%, 95% and 99% intervals of the terminal distribution."""
        return {
            'ci_90': {
                'lower': round(float(np.percentile(final_values, 5)), 2),
                'upper': round(float(np.percentile(final_values, 95)), 2)
            },
            'ci_95': {
                'lower': round(float(np.percentile(final_values, 2.5)), 2),
                'upper': round(float(np.percentile(final_values, 97.5)), 2)
            },
            'ci_99': {
                'lower': round(float(np.percentile(final_values, 0.5)), 2),
                'upper': round(float(np.percentile(final_values, 99.5)), 2)
            }
        }

    @staticmethod
    def _calculate_histogram(final_values: np.ndarray, num_bins: int = 50) -> Dict:
        """Histogram of terminal values for the distribution chart."""
        counts, bin_edges = np.histogram(final_values, bins=num_bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        percentages = (counts / len(final_values)) * 100

        return {
            'bins': bin_centers.tolist(),
            'frequencies': counts.tolist(),
            'percentages': percentages.tolist()
        }

    @staticmethod
    def calculate_risk_metrics(
        final_values: np.ndarray,
        total_contributions: float
    ) -> Dict:
        """
        Value at Risk and Conditional Value at Risk at the 5% level.

        VaR  = the 5th-percentile terminal value (95% of outcomes beat it).
        CVaR = the mean terminal value across the worst 5% of outcomes,
               i.e. the expected result given a bad tail.

        Loss figures are relative to total contributions, so a positive
        `var_loss_amount` means the 5% tail ends below the money paid in.
        """
        var_5 = float(np.percentile(final_values, 5))
        var_loss = total_contributions - var_5
        var_loss_percent = (var_loss / total_contributions) * 100 if total_contributions > 0 else 0.0

        worst_tail = final_values[final_values <= var_5]
        cvar_5 = float(np.mean(worst_tail)) if worst_tail.size > 0 else var_5
        cvar_loss = total_contributions - cvar_5
        cvar_loss_percent = (cvar_loss / total_contributions) * 100 if total_contributions > 0 else 0.0

        return {
            'var_5_percent': round(var_5, 2),
            'var_loss_amount': round(var_loss, 2),
            'var_loss_percent': round(var_loss_percent, 2),
            'cvar_5_percent': round(cvar_5, 2),
            'cvar_loss_amount': round(cvar_loss, 2),
            'cvar_loss_percent': round(cvar_loss_percent, 2)
        }
