/**
 * Portfolio Analytics Page
 * Displays portfolio risk analysis with metrics and visualizations
 */

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import portfolioAnalysisService from '../services/portfolioAnalysisService';

const PortfolioAnalytics = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [sampleParams, setSampleParams] = useState({
    initial_value: 100000,
    days: 252,
    volatility: 0.15,
    drift: 0.10,
  });

  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  useEffect(() => {
    fetchLatestAnalysis();
  }, []);

  const fetchLatestAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await portfolioAnalysisService.getLatestAnalysis();
      setAnalysis(data);
      
      // Use cached AI explanation from response if available
      if (data && data.ai_explanation) {
        setAiExplanation(data.ai_explanation);
      } else if (data) {
        // If no cached AI, fetch it (will be generated and cached by backend)
        fetchAIExplanation();
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError('No analysis found. Generate sample data or analyze your portfolio.');
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch analysis');
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
      const data = await portfolioAnalysisService.explainAnalysis();
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

  const handleGenerateAndAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      // Generate sample data
      const sampleData = await portfolioAnalysisService.generateSampleData(sampleParams);
      
      // Analyze the generated data
      const analysisResult = await portfolioAnalysisService.analyzePortfolio(
        sampleData.portfolio_data
      );
      
      setAnalysis(analysisResult);
      
      // Automatically fetch AI explanation after analysis
      fetchAIExplanation();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate and analyze data');
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    const colors = {
      'Low': 'text-green-600 bg-green-50 border-green-200',
      'Moderate': 'text-yellow-600 bg-yellow-50 border-yellow-200',
      'High': 'text-orange-600 bg-orange-50 border-orange-200',
      'Very High': 'text-red-600 bg-red-50 border-red-200',
    };
    return colors[riskLevel] || colors['Moderate'];
  };

  const getRiskScoreColor = (score) => {
    if (score < 30) return '#10b981'; // Green
    if (score < 50) return '#f59e0b'; // Yellow
    if (score < 70) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getMetricColor = (value, isPositive) => {
    if (isPositive) {
      return value >= 0 ? 'text-green-600' : 'text-red-600';
    }
    return value <= 0 ? 'text-green-600' : 'text-red-600';
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
        <h1>Portfolio Risk Analysis</h1>
        <p className="text-secondary-600">
          Comprehensive risk metrics and performance analysis
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Sample Data Generator */}
      <Card title="Generate Sample Portfolio Data" className="mb-6">
        <div className="space-y-4">
          <p className="text-sm text-secondary-600">
            Generate sample portfolio data to test the risk analysis features.
          </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Initial Value (₹)
                </label>
                <input
                  type="number"
                  value={sampleParams.initial_value}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    initial_value: parseFloat(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Days (30-1260)
                </label>
                <input
                  type="number"
                  min="30"
                  max="1260"
                  value={sampleParams.days}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    days: parseInt(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Volatility (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={sampleParams.volatility}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    volatility: parseFloat(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Expected Return (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="-1"
                  max="1"
                  value={sampleParams.drift}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    drift: parseFloat(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <Button
              onClick={handleGenerateAndAnalyze}
              disabled={analyzing}
              className="w-full"
            >
              {analyzing ? 'Generating & Analyzing...' : 'Generate & Analyze Sample Data'}
            </Button>
          </div>
        </Card>

      {/* Analysis Results */}
      {analysis && (
        <>
          {/* Risk Score Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card className="lg:col-span-1">
              <h3 className="text-lg font-semibold mb-4">Risk Score</h3>
              <div className="flex flex-col items-center">
                <div className="relative w-40 h-40 mb-4">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="#e5e7eb"
                      strokeWidth="12"
                      fill="none"
                    />
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke={getRiskScoreColor(analysis.risk_score)}
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={`${(analysis.risk_score / 100) * 439.8} 439.8`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="text-4xl font-bold" style={{ color: getRiskScoreColor(analysis.risk_score) }}>
                      {analysis.risk_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-secondary-600">/ 100</div>
                  </div>
                </div>
                <div className={`px-6 py-2 rounded-full border-2 font-semibold ${getRiskColor(analysis.risk_level)}`}>
                  {analysis.risk_level} Risk
                </div>
              </div>
            </Card>

            <Card className="lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Risk Interpretation</h3>
              <p className="text-secondary-700 mb-4">{analysis.interpretation.description}</p>
              
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-secondary-700 mb-2">Characteristics:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {analysis.interpretation.characteristics.map((char, idx) => (
                    <li key={idx} className="text-sm text-secondary-600">{char}</li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold text-secondary-700 mb-2">Recommendations:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {analysis.interpretation.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-secondary-600">{rec}</li>
                  ))}
                </ul>
              </div>
            </Card>
          </div>

          {/* Risk Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Volatility</h3>
                <span className="text-2xl">📊</span>
              </div>
              <div className="text-3xl font-bold text-primary-600 mb-1">
                {analysis.volatility_percent.toFixed(2)}%
              </div>
              <p className="text-xs text-secondary-600">
                Annualized standard deviation of returns
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  {analysis.volatility_percent < 10 ? 'Low volatility' :
                   analysis.volatility_percent < 20 ? 'Moderate volatility' :
                   analysis.volatility_percent < 30 ? 'High volatility' :
                   'Very high volatility'}
                </p>
              </div>
            </Card>

            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Sharpe Ratio</h3>
                <span className="text-2xl">📈</span>
              </div>
              <div className={`text-3xl font-bold mb-1 ${
                analysis.sharpe_ratio > 2 ? 'text-green-600' :
                analysis.sharpe_ratio > 1 ? 'text-yellow-600' :
                analysis.sharpe_ratio > 0 ? 'text-orange-600' :
                'text-red-600'
              }`}>
                {analysis.sharpe_ratio.toFixed(2)}
              </div>
              <p className="text-xs text-secondary-600">
                Risk-adjusted return metric
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  {analysis.sharpe_ratio > 2 ? 'Excellent' :
                   analysis.sharpe_ratio > 1 ? 'Good' :
                   analysis.sharpe_ratio > 0 ? 'Fair' :
                   'Poor'} risk-adjusted returns
                </p>
              </div>
            </Card>

            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Max Drawdown</h3>
                <span className="text-2xl">📉</span>
              </div>
              <div className={`text-3xl font-bold mb-1 ${getMetricColor(analysis.max_drawdown_percent, false)}`}>
                {analysis.max_drawdown_percent.toFixed(2)}%
              </div>
              <p className="text-xs text-secondary-600">
                Largest peak-to-trough decline
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  {Math.abs(analysis.max_drawdown_percent) < 10 ? 'Low drawdown' :
                   Math.abs(analysis.max_drawdown_percent) < 20 ? 'Moderate drawdown' :
                   Math.abs(analysis.max_drawdown_percent) < 30 ? 'High drawdown' :
                   'Severe drawdown'}
                </p>
              </div>
            </Card>

            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Total Return</h3>
                <span className="text-2xl">💰</span>
              </div>
              <div className={`text-3xl font-bold mb-1 ${getMetricColor(analysis.total_return, true)}`}>
                {analysis.total_return > 0 ? '+' : ''}{analysis.total_return.toFixed(2)}%
              </div>
              <p className="text-xs text-secondary-600">
                Overall portfolio return
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  Avg: {analysis.average_return_percent.toFixed(2)}% annually
                </p>
              </div>
            </Card>
          </div>

          {/* Additional Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <Card title="Performance Metrics">
              <div className="space-y-3">
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Average Return (Annual)</span>
                  <span className={`font-semibold ${getMetricColor(analysis.average_return_percent, true)}`}>
                    {analysis.average_return_percent > 0 ? '+' : ''}{analysis.average_return_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Risk-Free Rate</span>
                  <span className="font-semibold text-secondary-900">
                    {(analysis.risk_free_rate * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Excess Return</span>
                  <span className={`font-semibold ${getMetricColor(analysis.average_return_percent - (analysis.risk_free_rate * 100), true)}`}>
                    {(analysis.average_return_percent - (analysis.risk_free_rate * 100)).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-secondary-700">Return per Unit Risk</span>
                  <span className="font-semibold text-secondary-900">
                    {(analysis.average_return_percent / analysis.volatility_percent).toFixed(2)}
                  </span>
                </div>
              </div>
            </Card>

            <Card title="Analysis Details">
              <div className="space-y-3">
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Data Points</span>
                  <span className="font-semibold text-secondary-900">{analysis.data_points}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Analysis Period</span>
                  <span className="font-semibold text-secondary-900">
                    {analysis.analysis_period_days} days
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Trading Days</span>
                  <span className="font-semibold text-secondary-900">
                    ~{Math.floor(analysis.analysis_period_days * 252 / 365)} days
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-secondary-700">Annualization Factor</span>
                  <span className="font-semibold text-secondary-900">√252</span>
                </div>
              </div>
            </Card>
          </div>

          {/* AI Insights Card */}
          <Card title="AI Risk Analysis" className="mb-6">
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
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 px-4 py-3 mb-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">🤖</span>
                    <span className="font-semibold text-blue-900">AI-Powered Risk Insights</span>
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
            <Button onClick={handleGenerateAndAnalyze} disabled={analyzing}>
              {analyzing ? 'Analyzing...' : 'Generate New Analysis'}
            </Button>
            <Button variant="outline" onClick={fetchLatestAnalysis}>
              Refresh
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default PortfolioAnalytics;
