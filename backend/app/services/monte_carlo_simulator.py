"""
Monte Carlo Portfolio Simulation Service
Generates portfolio simulations using Monte Carlo method
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class MonteCarloSimulator:
    """
    Monte Carlo simulator for portfolio projections
    Simulates portfolio performance over time using random walk with drift
    """
    
    @staticmethod
    def run_simulation(
        initial_investment: float,
        expected_return: float,
        volatility: float,
        years: int,
        num_simulations: int = 10000,
        monthly_contribution: float = 0.0
    ) -> Dict:
        """
        Run Monte Carlo simulation for portfolio
        
        Args:
            initial_investment: Starting portfolio value
            expected_return: Expected annual return (decimal, e.g., 0.12 for 12%)
            volatility: Annual volatility/standard deviation (decimal, e.g., 0.15 for 15%)
            years: Investment duration in years
            num_simulations: Number of simulation runs (default: 10000)
            monthly_contribution: Monthly contribution amount (default: 0)
            
        Returns:
            dict with simulation results, statistics, and scenarios
        """
        if initial_investment <= 0:
            raise ValueError("Initial investment must be greater than 0")
        
        if years <= 0 or years > 50:
            raise ValueError("Years must be between 1 and 50")
        
        if num_simulations < 1000 or num_simulations > 50000:
            raise ValueError("Number of simulations must be between 1000 and 50000")
        
        # Calculate number of periods (monthly)
        num_periods = years * 12
        
        # Convert annual metrics to monthly
        monthly_return = expected_return / 12
        monthly_volatility = volatility / np.sqrt(12)
        
        # Generate random returns for all simulations
        # Shape: (num_simulations, num_periods)
        random_returns = np.random.normal(
            monthly_return,
            monthly_volatility,
            size=(num_simulations, num_periods)
        )
        
        # Initialize portfolio values
        portfolio_values = np.zeros((num_simulations, num_periods + 1))
        portfolio_values[:, 0] = initial_investment
        
        # Run simulations
        for period in range(num_periods):
            # Calculate returns for this period
            period_returns = random_returns[:, period]
            
            # Update portfolio values with returns
            portfolio_values[:, period + 1] = portfolio_values[:, period] * (1 + period_returns)
            
            # Add monthly contribution
            if monthly_contribution > 0:
                portfolio_values[:, period + 1] += monthly_contribution
        
        # Get final values for all simulations
        final_values = portfolio_values[:, -1]
        
        # Calculate statistics
        statistics = MonteCarloSimulator._calculate_statistics(
            final_values=final_values,
            initial_investment=initial_investment,
            monthly_contribution=monthly_contribution,
            num_periods=num_periods
        )
        
        # Get scenario projections
        scenarios = MonteCarloSimulator._calculate_scenarios(final_values)
        
        # Calculate confidence intervals
        confidence_intervals = MonteCarloSimulator._calculate_confidence_intervals(final_values)
        
        # Get distribution data for charting (sample every N simulations for performance)
        sample_interval = max(1, num_simulations // 100)  # Max 100 lines on chart
        sampled_simulations = portfolio_values[::sample_interval, :]
        
        # Create time periods array (in months)
        time_periods = list(range(num_periods + 1))
        
        # Prepare simulation paths for charting
        simulation_paths = []
        for sim_path in sampled_simulations:
            simulation_paths.append(sim_path.tolist())
        
        # Calculate percentile paths for charting
        percentile_paths = {
            'p10': np.percentile(portfolio_values, 10, axis=0).tolist(),
            'p25': np.percentile(portfolio_values, 25, axis=0).tolist(),
            'p50': np.percentile(portfolio_values, 50, axis=0).tolist(),  # Median
            'p75': np.percentile(portfolio_values, 75, axis=0).tolist(),
            'p90': np.percentile(portfolio_values, 90, axis=0).tolist(),
        }
        
        # Calculate distribution histogram data
        histogram_data = MonteCarloSimulator._calculate_histogram(final_values)
        
        return {
            'statistics': statistics,
            'scenarios': scenarios,
            'confidence_intervals': confidence_intervals,
            'simulation_paths': simulation_paths[:20],  # Only first 20 for performance
            'percentile_paths': percentile_paths,
            'time_periods': time_periods,
            'histogram_data': histogram_data,
            'num_simulations': num_simulations,
            'years': years,
            'initial_investment': initial_investment,
            'monthly_contribution': monthly_contribution,
            'expected_return': expected_return,
            'volatility': volatility
        }
    
    @staticmethod
    def _calculate_statistics(
        final_values: np.ndarray,
        initial_investment: float,
        monthly_contribution: float,
        num_periods: int
    ) -> Dict:
        """Calculate statistical metrics from simulation results"""
        
        total_contributions = initial_investment + (monthly_contribution * num_periods)
        
        mean_value = float(np.mean(final_values))
        median_value = float(np.median(final_values))
        std_value = float(np.std(final_values))
        min_value = float(np.min(final_values))
        max_value = float(np.max(final_values))
        
        # Calculate returns
        mean_return = ((mean_value - total_contributions) / total_contributions) * 100
        median_return = ((median_value - total_contributions) / total_contributions) * 100
        
        # Calculate probability of profit
        probability_of_profit = float(np.sum(final_values > total_contributions) / len(final_values)) * 100
        
        # Calculate probability of doubling investment
        probability_of_doubling = float(np.sum(final_values >= total_contributions * 2) / len(final_values)) * 100
        
        # Calculate probability of loss
        probability_of_loss = float(np.sum(final_values < total_contributions) / len(final_values)) * 100
        
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
        """Calculate best, average, and worst case scenarios"""
        
        # Best case: 95th percentile
        best_case = float(np.percentile(final_values, 95))
        
        # Average case: 50th percentile (median)
        average_case = float(np.percentile(final_values, 50))
        
        # Worst case: 5th percentile
        worst_case = float(np.percentile(final_values, 5))
        
        return {
            'best_case': round(best_case, 2),
            'average_case': round(average_case, 2),
            'worst_case': round(worst_case, 2)
        }
    
    @staticmethod
    def _calculate_confidence_intervals(final_values: np.ndarray) -> Dict:
        """Calculate confidence intervals"""
        
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
        """Calculate histogram data for distribution chart"""
        
        # Create histogram
        counts, bin_edges = np.histogram(final_values, bins=num_bins)
        
        # Calculate bin centers
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Convert to percentages
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
        """Calculate risk metrics from simulation results"""
        
        # Value at Risk (VaR) - 5th percentile
        var_5 = float(np.percentile(final_values, 5))
        var_loss = total_contributions - var_5
        var_loss_percent = (var_loss / total_contributions) * 100 if total_contributions > 0 else 0
        
        # Conditional Value at Risk (CVaR) - average of worst 5%
        worst_5_percent = final_values[final_values <= var_5]
        cvar_5 = float(np.mean(worst_5_percent)) if len(worst_5_percent) > 0 else var_5
        cvar_loss = total_contributions - cvar_5
        cvar_loss_percent = (cvar_loss / total_contributions) * 100 if total_contributions > 0 else 0
        
        return {
            'var_5_percent': round(var_5, 2),
            'var_loss_amount': round(var_loss, 2),
            'var_loss_percent': round(var_loss_percent, 2),
            'cvar_5_percent': round(cvar_5, 2),
            'cvar_loss_amount': round(cvar_loss, 2),
            'cvar_loss_percent': round(cvar_loss_percent, 2)
        }
