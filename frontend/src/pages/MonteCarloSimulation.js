/**
 * Monte Carlo Simulation Page
 * Portfolio simulation with 10,000 Monte Carlo runs
 */

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import monteCarloService from '../services/monteCarloService';

const MonteCarloSimulation = () => {
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState(null);
  const [simulationHistory, setSimulationHistory] = useState([]);
  
  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');
  
  const [params, setParams] = useState({
    initial_investment: 100000,
    expected_return: 0.12,
    volatility: 0.15,
    years: 10,
    num_simulations: 10000,
    monthly_contribution: 0,
    simulation_name: '',
    notes: ''
  });

  useEffect(() => {
    fetchLatestSimulation();
    fetchSimulationHistory();
  }, []);

  const fetchLatestSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await monteCarloService.getLatestSimulation();
      setSimulation(data);
      
      // Use cached AI explanation from response if available
      if (data && data.ai_explanation) {
        setAiExplanation(data.ai_explanation);
      } else if (data) {
        // If no cached AI, fetch it (will be generated and cached by backend)
        fetchAIExplanation();
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError('No simulations found. Run your first simulation below.');
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch simulation');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchAIExplanation = async () => {
    setAiLoading(true);
    setAiError('');
    setAiExplanation('');

    try {
      const data = await monteCarloService.explainSimulation();
      if (data.ai_available && data.ai_explanation) {
        setAiExplanation(data.ai_explanation);
      } else {
        setAiError('AI insights are currently unavailable.');
      }
    } catch (err) {
      console.error('AI explanation error:', err);
      setAiError('AI insights are currently unavailable.');
    } finally {
      setAiLoading(false);
    }
  };

  const fetchSimulationHistory = async () => {
    try {
      const data = await monteCarloService.getSimulations(10);
      setSimulationHistory(data);
    } catch (err) {
      console.log('No simulation history');
    }
  };

  const handleRunSimulation = async () => {
    setSimulating(true);
    setError(null);
    try {
      const result = await monteCarloService.runSimulation(params, true);
      setSimulation(result);
      fetchSimulationHistory(); // Refresh history
      
      // Automatically fetch AI explanation after simulation
      fetchAIExplanation();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run simulation');
    } finally {
      setSimulating(false);
    }
  };

  const formatCurrency = (value) => {
    return `₹${(value / 100000).toFixed(2)}L`;
  };

  const formatPercent = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Prepare data for percentile chart
  const preparePercentileChartData = () => {
    if (!simulation || !simulation.percentile_paths) return [];
    
    const data = [];
    const periods = simulation.time_periods || [];
    
    for (let i = 0; i < periods.length; i++) {
      data.push({
        period: periods[i],
        p10: simulation.percentile_paths.p10[i],
        p25: simulation.percentile_paths.p25[i],
        p50: simulation.percentile_paths.p50[i],
        p75: simulation.percentile_paths.p75[i],
        p90: simulation.percentile_paths.p90[i]
      });
    }
    
    return data;
  };

  // Prepare data for histogram
  const prepareHistogramData = () => {
    if (!simulation || !simulation.histogram_data) return [];
    
    const data = [];
    const bins = simulation.histogram_data.bins || [];
    const percentages = simulation.histogram_data.percentages || [];
    
    for (let i = 0; i < bins.length; i++) {
      data.push({
        value: bins[i],
        percentage: percentages[i]
      });
    }
    
    return data;
  };

  const getScenarioColor = (type) => {
    const colors = {
      best: '#10b981',
      average: '#3b82f6',
      worst: '#ef4444'
    };
    return colors[type] || '#6b7280';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1>Monte Carlo Portfolio Simulation</h1>
        <p className="text-secondary-600">
          Run 10,000 simulations to project portfolio growth scenarios
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Simulation Parameters */}
      <Card title="Simulation Parameters" className="mb-6">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Initial Investment (₹)
              </label>
              <input
                type="number"
                value={params.initial_investment}
                onChange={(e) => setParams({...params, initial_investment: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Expected Annual Return (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={(params.expected_return * 100).toFixed(1)}
                onChange={(e) => setParams({...params, expected_return: parseFloat(e.target.value) / 100})}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Volatility (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={(params.volatility * 100).toFixed(1)}
                onChange={(e) => setParams({...params, volatility: parseFloat(e.target.value) / 100})}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Investment Duration (Years)
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={params.years}
                onChange={(e) => setParams({...params, years: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Monthly Contribution (₹)
              </label>
              <input
                type="number"
                value={params.monthly_contribution}
                onChange={(e) => setParams({...params, monthly_contribution: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Number of Simulations
              </label>
              <input
                type="number"
                min="1000"
                max="50000"
                step="1000"
                value={params.num_simulations}
                onChange={(e) => setParams({...params, num_simulations: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Simulation Name (Optional)
              </label>
              <input
                type="text"
                value={params.simulation_name}
                onChange={(e) => setParams({...params, simulation_name: e.target.value})}
                placeholder="e.g., Retirement Portfolio 2035"
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Notes (Optional)
              </label>
              <input
                type="text"
                value={params.notes}
                onChange={(e) => setParams({...params, notes: e.target.value})}
                placeholder="Add notes about this simulation"
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          
          <Button
            onClick={handleRunSimulation}
            disabled={simulating}
            className="w-full"
          >
            {simulating ? 'Running Simulation...' : `Run ${params.num_simulations.toLocaleString()} Simulations`}
          </Button>
        </div>
      </Card>

      {/* Results */}
      {simulation && (
        <>
          {/* Scenarios Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <Card>
              <div className="text-center">
                <div className="text-sm font-medium text-secondary-600 mb-2">
                  Best Case (95th Percentile)
                </div>
                <div className="text-3xl font-bold mb-1" style={{ color: getScenarioColor('best') }}>
                  {formatCurrency(simulation.scenarios.best_case)}
                </div>
                <div className="text-xs text-secondary-500">
                  Top 5% of outcomes
                </div>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <div className="text-sm font-medium text-secondary-600 mb-2">
                  Average Case (Median)
                </div>
                <div className="text-3xl font-bold mb-1" style={{ color: getScenarioColor('average') }}>
                  {formatCurrency(simulation.scenarios.average_case)}
                </div>
                <div className="text-xs text-secondary-500">
                  50th percentile outcome
                </div>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <div className="text-sm font-medium text-secondary-600 mb-2">
                  Worst Case (5th Percentile)
                </div>
                <div className="text-3xl font-bold mb-1" style={{ color: getScenarioColor('worst') }}>
                  {formatCurrency(simulation.scenarios.worst_case)}
                </div>
                <div className="text-xs text-secondary-500">
                  Bottom 5% of outcomes
                </div>
              </div>
            </Card>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <Card>
              <div className="text-sm font-medium text-secondary-600 mb-1">Mean Value</div>
              <div className="text-2xl font-bold text-primary-600">
                {formatCurrency(simulation.statistics.mean_value)}
              </div>
              <div className="text-xs text-secondary-500 mt-1">
                Average of all simulations
              </div>
            </Card>

            <Card>
              <div className="text-sm font-medium text-secondary-600 mb-1">Total Invested</div>
              <div className="text-2xl font-bold text-secondary-900">
                {formatCurrency(simulation.statistics.total_contributions)}
              </div>
              <div className="text-xs text-secondary-500 mt-1">
                Initial + contributions
              </div>
            </Card>

            <Card>
              <div className="text-sm font-medium text-secondary-600 mb-1">Profit Probability</div>
              <div className="text-2xl font-bold text-green-600">
                {simulation.statistics.probability_of_profit.toFixed(1)}%
              </div>
              <div className="text-xs text-secondary-500 mt-1">
                Chance of positive return
              </div>
            </Card>

            <Card>
              <div className="text-sm font-medium text-secondary-600 mb-1">Doubling Probability</div>
              <div className="text-2xl font-bold text-blue-600">
                {simulation.statistics.probability_of_doubling.toFixed(1)}%
              </div>
              <div className="text-xs text-secondary-500 mt-1">
                Chance of 2x returns
              </div>
            </Card>
          </div>

          {/* Percentile Projection Chart */}
          <Card title="Future Wealth Projections" className="mb-6">
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={preparePercentileChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="period" 
                  label={{ value: 'Months', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  tickFormatter={(value) => `₹${(value / 100000).toFixed(0)}L`}
                  label={{ value: 'Portfolio Value', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value) => formatCurrency(value)}
                  labelFormatter={(label) => `Month ${label}`}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="p90" 
                  stackId="1"
                  stroke="#10b981" 
                  fill="#10b98120" 
                  name="90th Percentile"
                />
                <Area 
                  type="monotone" 
                  dataKey="p75" 
                  stackId="2"
                  stroke="#3b82f6" 
                  fill="#3b82f620" 
                  name="75th Percentile"
                />
                <Area 
                  type="monotone" 
                  dataKey="p50" 
                  stackId="3"
                  stroke="#f59e0b" 
                  fill="#f59e0b20" 
                  name="Median (50th)"
                />
                <Area 
                  type="monotone" 
                  dataKey="p25" 
                  stackId="4"
                  stroke="#f97316" 
                  fill="#f9731620" 
                  name="25th Percentile"
                />
                <Area 
                  type="monotone" 
                  dataKey="p10" 
                  stackId="5"
                  stroke="#ef4444" 
                  fill="#ef444420" 
                  name="10th Percentile"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Probability Distribution */}
          <Card title="Probability Distribution of Final Values" className="mb-6">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={prepareHistogramData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="value" 
                  tickFormatter={(value) => `₹${(value / 100000).toFixed(0)}L`}
                  label={{ value: 'Final Portfolio Value', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value) => `${value.toFixed(2)}%`}
                  labelFormatter={(label) => `Value: ${formatCurrency(label)}`}
                />
                <Bar dataKey="percentage" fill="#3b82f6" name="Probability" />
              </BarChart>
            </ResponsiveContainer>
            
            <div className="mt-4 text-center text-sm text-secondary-600">
              Distribution of {simulation.num_simulations.toLocaleString()} simulation outcomes
            </div>
          </Card>

          {/* Confidence Intervals */}
          <Card title="Confidence Intervals" className="mb-6">
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-green-900">90% Confidence Interval</span>
                  <span className="text-sm text-green-700">90% chance of falling in this range</span>
                </div>
                <div className="flex justify-between text-2xl font-bold text-green-600">
                  <span>{formatCurrency(simulation.confidence_intervals.ci_90.lower)}</span>
                  <span>—</span>
                  <span>{formatCurrency(simulation.confidence_intervals.ci_90.upper)}</span>
                </div>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-blue-900">95% Confidence Interval</span>
                  <span className="text-sm text-blue-700">95% chance of falling in this range</span>
                </div>
                <div className="flex justify-between text-2xl font-bold text-blue-600">
                  <span>{formatCurrency(simulation.confidence_intervals.ci_95.lower)}</span>
                  <span>—</span>
                  <span>{formatCurrency(simulation.confidence_intervals.ci_95.upper)}</span>
                </div>
              </div>

              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-purple-900">99% Confidence Interval</span>
                  <span className="text-sm text-purple-700">99% chance of falling in this range</span>
                </div>
                <div className="flex justify-between text-2xl font-bold text-purple-600">
                  <span>{formatCurrency(simulation.confidence_intervals.ci_99.lower)}</span>
                  <span>—</span>
                  <span>{formatCurrency(simulation.confidence_intervals.ci_99.upper)}</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Additional Statistics */}
          <Card title="Detailed Statistics" className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex justify-between pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Mean Return</span>
                  <span className="font-semibold text-secondary-900">
                    {simulation.statistics.mean_return_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Median Return</span>
                  <span className="font-semibold text-secondary-900">
                    {simulation.statistics.median_return_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Standard Deviation</span>
                  <span className="font-semibold text-secondary-900">
                    {formatCurrency(simulation.statistics.std_deviation)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-secondary-700">Range</span>
                  <span className="font-semibold text-secondary-900">
                    {formatCurrency(simulation.statistics.min_value)} - {formatCurrency(simulation.statistics.max_value)}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Initial Investment</span>
                  <span className="font-semibold text-secondary-900">
                    {formatCurrency(simulation.initial_investment)}
                  </span>
                </div>
                <div className="flex justify-between pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Monthly Contribution</span>
                  <span className="font-semibold text-secondary-900">
                    ₹{simulation.monthly_contribution.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Expected Return (Annual)</span>
                  <span className="font-semibold text-secondary-900">
                    {formatPercent(simulation.expected_return)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-secondary-700">Volatility (Annual)</span>
                  <span className="font-semibold text-secondary-900">
                    {formatPercent(simulation.volatility)}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* AI Insights Card */}
          <Card title="AI Investment Strategy Insights" className="mb-6">
            {aiLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loading message="Generating AI insights..." />
              </div>
            ) : aiError ? (
              <div className="text-center py-6">
                <p className="text-secondary-600 mb-4">{aiError}</p>
                <Button variant="outline" onClick={fetchAIExplanation} size="sm">
                  Retry AI Explanation
                </Button>
              </div>
            ) : aiExplanation ? (
              <div className="prose max-w-none">
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-l-4 border-purple-500 px-4 py-3 mb-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">🤖</span>
                    <span className="font-semibold text-purple-900">AI-Powered Simulation Analysis</span>
                  </div>
                </div>
                <div className="text-secondary-700 leading-relaxed">
                  <ReactMarkdown>
                    {aiExplanation}
                  </ReactMarkdown>
                </div>
              </div>
            ) : null}
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button onClick={handleRunSimulation} disabled={simulating}>
              {simulating ? 'Running...' : 'Run New Simulation'}
            </Button>
            <Button variant="outline" onClick={fetchLatestSimulation}>
              Refresh
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default MonteCarloSimulation;
